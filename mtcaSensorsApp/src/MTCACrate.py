#!/usr/bin/env python
# File: MTCACrate.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get sensor information for microTCA crate.
#

from devsup.db import IOScanListBlock
from subprocess import check_output

AMC_SLOT_OFFSET = 96
AMC_BUS_ID = 193

SENSOR_NAMES = {
    '12 V PP': '12V0',
    '12V PP': '12V0',
    '12 V AMC': '12V0',
    '3.3 V PP': '3V3',
    '3.3V MP': '3V3',
    '2.5 V': '2V5',
    '2.5V': '2V5',
    '1.8 V': '1V8',
    '1.8V': '1V8',
    '1.5V DDR3': '1V5',
    '1.0V CORE': '1V0',
    'Current 12 V': '12V0CURRENT',
    'Current 3.3 V': '3V3CURRENT',
    'Current 1.2 V': '1V2CURRENT',
    'Inlet': 'TEMP_INLET',
    'Temp 1 (inlet)': 'TEMP_INLET',
    'Outlet': 'TEMP_OUTLET',
    'Temp 2 (outlet)': 'TEMP_OUTLET',
    'DC/DC Inlet': 'TEMP1',
    'FMC1': 'TEMP2',
    'FMC2': 'TEMP3',
    'CPLD': 'TEMP4',
    'FPGA V5': 'TEMP5',
    'FPGA S6': 'TEMP6'
}

ALARMS = {
    'Lower Critical': 'lolo',
    'Lower Non-Critical': 'low',
    'Upper Non-Critical': 'high',
    'Upper Critical': 'hihi'
}

EGU = { 
    'Volts': 'V',
    'Amps': 'A',
    'degrees C': 'C',
    'unspecified': '',
    'RPM': 'RPM'
}

def get_crate():
    """
    Find existing crate object, or create new one.

    Args:
        host: host name of crate MCH

    Returns: 
        MTCACrate object
    """
    
    try:
        return _crate
    except:
        pass

class Sensor():
    """
    Sensor information
    """
    def __init__(self, name):
        self.name = name
        self.value = 0.0
        self.lolo = 0.0
        self.low = 0.0
        self.high = 0.0
        self.hihi = 0.0
        self.alarms_set = False

class AMC_Slot():
    """
    AMC_Slot information
    """

    def __init__(self, id = None, name = None, slot = None, crate = None):
        """
        AMC_Slot class initializer

        Args:
            id (str): AMC_Slot ID (e.g., 193.101)
            name (str): AMC card name
            slot(int): AMC slot number
            crate(obj): reference to crate object

        Returns: 
            Nothing
        """
        self.id = id
        self.name = name
        self.slot  = slot
        self.crate = crate

        # Properties for storing sensor values
        self.sensors = {}

    def __str__(self):
        """
        AMC_Slot class printout
        
        Args:
            None

        Returns:
            String representation of AMC_Slot
        """
        return "ID: {}, Name: {}".format(self.id, self.name)

    def read_sensors(self):
        """
        Read the sensors for this AMC Slot 

        Args:
            None

        Returns:
            Nothing
        """

        # Create the IPMI tool command
        command = []
        command.append("ipmitool")
        command.append("-H")
        command.append(self.crate.host)
        command.append("-U")
        command.append(self.crate.user)
        command.append("-P")
        command.append(self.crate.password)
        command.append("sdr")
        command.append("entity")
        command.append(self.id)

        result = check_output(command)
        
        for line in result.splitlines():
            try:
                line_strip = [x.strip() for x in line.split('|')]
                sensor_name, sensor_id, status, fru_id, val = line_strip
                value, egu = val.split(' ', 1)
                # Check if the sensor name is in the list we know about
                if sensor_name in SENSOR_NAMES.keys():
                    sensor_type = SENSOR_NAMES[sensor_name]
                    # Check if we have already created this sensor
                    if not sensor_type in self.sensors.keys():
                        self.sensors[sensor_type] = Sensor(sensor_name)
                
                    self.sensors[sensor_type].value = float(value)

                    # Get the simplified engineering units
                    if egu in EGU.keys():
                        self.sensors[sensor_type].egu = EGU[egu]
                    else:
                        self.sensors[sensor_type].egu = egu

                    if not self.sensors[sensor_type].alarms_set:
                        self.set_alarms(sensor_name)
                        self.sensors[sensor_type].alarms_set = True
            except ValueError:
                pass

    def set_alarms(self, name):
        """
        Function to set alarm setpoints in AI records

        Args:
            name: sensor name

        Returns:
            Nothing
        """
        command = []
        command.append("ipmitool")
        command.append("-H")
        command.append(self.crate.host)
        command.append("-U")
        command.append(self.crate.user)
        command.append("-P")
        command.append(self.crate.password)
        command.append("sensor")
        command.append("get")
        command.append(name)

        result = check_output(command)

        for line in result.splitlines():
            try:
                description, value = [x.strip() for x in line.split(':',1)]
                if description in ALARMS.keys():
                    sensor_type = SENSOR_NAMES[name]
                    setattr(self.sensors[sensor_type], ALARMS[description], float(value))
                    self.sensors[sensor_type].alarms_set = True       
            except ValueError:
                pass


        
class MTCACrate():
    """
    Class for holding microTCA crate information, including AMC Slot list
    """
    
    def __init__(self):
        """
        Initializer for MTCACrate object.

        Args:
            host: host name of MCH in crate

        Returns:
            Nothing
        """

        self.host = None
        self.user = None
        self.password = None

        # Initialize dict of AMC Slots
        self.amc_slots = {}
        self.amc_slots_inited = False

        # Create scan list for I/O Intr records
        self.scan_list = IOScanListBlock()

    def populate_amc_slot_list(self):
        """ 
        Call MCH and get list of AMC slots

        Args:   
            None

        Returns:
            Nothing
        """

        if self.host != None and self.user != None and self.password != None:
            command = []
            command.append("ipmitool")
            command.append("-H")
            command.append(self.host)
            command.append("-U")
            command.append(self.user)
            command.append("-P")
            command.append(self.password)
            command.append("sdr")
            command.append("elist")
            command.append("fru")

            result = check_output(command)
            
            for line in result.splitlines():
                try:
                    name, ref, status, id, desc = line.split('|')
                    
                    # Get the AMC slot number
                    bus, slot = id.strip().split('.')
                    bus, slot = int(bus), int(slot)
                    slot -= AMC_SLOT_OFFSET
                    if bus == AMC_BUS_ID:
                        if slot not in self.amc_slots.keys():
                            self.amc_slots[slot] = AMC_Slot(
                                    name=name.strip(), 
                                    id=id.strip(), 
                                    slot=slot, 
                                    crate = self)
                except ValueError:
                    print "Couldn't parse {}".format(line)
            self.amc_slots_inited = True
        else:
            print("Crate information not populated")

    def read_sensors(self):
        """ 
        Call read all sensor values

        Args:   
            None

        Returns:
            Nothing
        """

        for slot in self.amc_slots:
            self.amc_slots[slot].read_sensors()

_crate = MTCACrate()

class MTCACrateReader():
    """
    Class for interfacing to EPICS PVs for MTCA crate
    """

    # Allow us to write direct to rec.VAL
    raw = True

    def __init__(self, rec, args):
        """
        Initializer class

        Args:
            rec: pyDevSup record object
            fn (str): function to be called
            args (str): arguments from EPICS record
                slot (int, optional): amc slot number 
                sensor(str, optional): sensor to read

        Returns:
            Nothing
        """

        args_list = args.split(None, 2)
        if len(args_list) == 3:
            fn, slot, sensor = args_list
        elif len(args_list) == 2:
            fn, slot = args_list
            sensor = None
        else:
            fn = args
            slot = 0
            sensor = None

        self.crate = get_crate()
        # Set up the function to be called when the record processes
        self.process = getattr(self, fn)
        # Allow for I/O Intr scanning
        self.allowScan = self.crate.scan_list.add
        self.slot = int(slot)
        self.sensor = sensor
        self.alarms_set = False

        # Set record invalid until it processes
        rec.UDF = 1

    def detach(self, rec):
        pass

    def set_host(self, rec, report):
        """
        Set host name

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.host = rec.VAL
        rec.UDF = 0

    def set_user(self, rec, report):
        """
        Set user name

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.user = rec.VAL
        rec.UDF = 0

    def set_password(self, rec, report):
        """
        Set password 

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.password = rec.VAL
        rec.UDF = 0

    def get_amc_slot_list(self, rec, report):
        """
        Get AMC_Slot info from crate

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.populate_amc_slot_list()
        rec.UDF = 0

    def read_sensors(self, rec, report):
        """
        Read all sensor values for this crate

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        try:
            self.crate.read_sensors()
            self.crate.scan_list.interrupt()
        except AttributeError:
            # TODO: Work out why we get this exception
            pass


    def get_val(self, rec, report):
        """ 
        Get sensor reading

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        valid_sensor = False

        if self.sensor != None:
            # Check if this card exists
            if self.slot in self.crate.amc_slots.keys():
                # Check if this is a valid sensor
                if self.sensor in self.crate.amc_slots[self.slot].sensors.keys():
                    if not self.alarms_set:
                        self.set_alarms(rec)
                    val = self.crate.amc_slots[self.slot].sensors[self.sensor].value
                    egu = self.crate.amc_slots[self.slot].sensors[self.sensor].egu
                    rec.VAL = val
                    rec.EGU = egu
                    rec.UDF = 0
                    valid_sensor = True
        if not valid_sensor:
            rec.VAL = 0
            rec.EGU = ''
            rec.UDF = 0

    def set_alarms(self, rec):
        """
        Set alarm values in PV

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        try:
            rec.LOLO = self.crate.amc_slots[self.slot].sensors[self.sensor].lolo
            rec.LOW = self.crate.amc_slots[self.slot].sensors[self.sensor].low
            rec.HIGH = self.crate.amc_slots[self.slot].sensors[self.sensor].high
            rec.HIHI = self.crate.amc_slots[self.slot].sensors[self.sensor].hihi
            rec.LLSV = 2 # MAJOR
            rec.LSV = 1 # MINOR
            rec.HSV = 1 # MINOR
            rec.HHSV = 2 # MAJOR
            self.alarms_set = True
        except KeyError as e:
            print "Caught KeyError: {}".format(e)
    
    def get_name(self, rec, report):
        """
        Get card name

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        # Check if this card exists
        if self.slot in self.crate.amc_slots.keys():
            rec.VAL = self.crate.amc_slots[self.slot].name
        else:
            rec.VAL = "Empty"

    def get_slot(self, rec, report):
        """
        Get card slot

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        # Check if this card exists
        if self.slot in self.crate.amc_slots.keys():
            rec.VAL = self.crate.amc_slots[self.slot].slot
        else:
            rec.VAL = -1
        # Make the record defined regardless of value
        rec.UDF = 0

build = MTCACrateReader

