#!/usr/bin/env python
# File: MTCACrate.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get FRU information for microTCA crate.
# FRU = Field Replaceable Unit
#

from devsup.db import IOScanListBlock
from subprocess import check_output

AMC_SLOT_OFFSET = 96

SENSOR_NAMES = {
        '12 V PP': '12V',
        '12 V AMC': '12V',
        '3.3 V PP': '3V3',
        '3.3 V MP': '3V3',
        '1.8 V': '1V8',
        '1.0 V CORE': '1V0'
        }

ALARMS = {
        'Lower Critical': 'lolo',
        'Lower Non-Critical': 'low',
        'Upper Non-Critical': 'high',
        'Upper Critical': 'hihi'
        }

#_crates = {}

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

class FRU():
    """
    FRU information
    """

    def __init__(self, id=None, name=None):
        """
        FRU class initializer

        Args:
            id (str): FRU ID (e.g., 192.101)
            name (str): FRU name
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
        FRU class printout
        
        Args:
            None

        Returns:
            String representation of FRU
        """
        return "ID: {}, Name: {}".format(self.id, self.name)

    def read_sensors(self):
        """
        Read the sensors for this FRU

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
                name, sensor_id, status, fru_id, val = line_strip
                value, egu = val.split(' ', 1)
                # Check if the sensor name is in the list we know about
                if sensor_name in SENSOR_NAMES.keys():
                    sensor_type = SENSOR_NAMES[name]
                    # Check if we have already created this sensor
                    if not sensor_type in self.sensors.keys():
                        self.sensors[sensor_type] = Sensor(name)
                    self.sensors[sensor_type].value = float(value)
                    self.sensors[sensor_type].egu = egu

                    if not self.sensors[sensor_type].alarms_set:
                        self.set_alarms(sensor_name)
                        self.set_alarms[sensor_type].alarms_set = True
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
                item, value = [x.strip() for x in line.split(':',1)]
                if item in ALARMS.keys():
                    sensor_type = SENSOR_NAMES[name]
                    setattr(self.sensors[sensor_type], ALARMS[item], float(value))
            except ValueError:
                pass

        self.sensors[name].alarms_set = True       

        
class MTCACrate():
    """
    Class for holding microTCA crate information, including FRU list
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

        # Initialize dict of FRUs
        self.frus = {}
        self.frus_inited = False

		# Create scan list for I/O Intr records
		self.scan_list = IOScanListBlock()

    def populate_fru_list(self):
        """ 
        Call MCH and get list of FRUs

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
                    slot = int(id.strip().split('.')[1])
                    slot -= AMC_SLOT_OFFSET
                    self.frus[slot] = FRU(
                            name=name.strip(), 
                            id=id.strip(), 
                            slot=slot, 
                            crate = self)
                    self.frus_inited = True
                except ValueError:
                    print "Couldn't parse {}".format(line)
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

        for slot in self.frus:
            self.frus[slot].read_sensors()


_crate = MTCACrate()

class MTCACrateReader():
    """
    Class for interfacing to EPICS PVs for MTCA crate
    """

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

    def get_fru_list(self, rec, report):
        """
        Get FRU info from crate

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.populate_fru_list()
        rec.UDF = 0

    def read_sensors(self, rec, report):
        """
        Read all sensor values for this crate

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
		self.crate.read_sensors()
		self.crate.scan_list.interrupt()


    def get_val(self, rec, report):
        """ 
        Get sensor reading

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        if not self.alarms_set:
            set_alarms(rec)

        rec.VAL = getattr(self.crate.frus[self.slot], self.sensor)
        rec.UDF = 0

    def set_alarms(self, rec):
        rec.LOLO = self.crate.frus[self.slot].sensors[self.sensor].lolo
        rec.LOW = self.crate.frus[self.slot].sensors[self.sensor].low
        rec.HIGH = self.crate.frus[self.slot].sensors[self.sensor].high
        rec.HIHI = self.crate.frus[self.slot].sensors[self.sensor].hihi
        rec.LLSV = 2 # MAJOR
        rec.LSV = 1 # MINOR
        rec.HSV = 1 # MINOR
        rec.HHSV = 2 # MAJOR
        self.alarms_set = True

build = MTCACrateReader

