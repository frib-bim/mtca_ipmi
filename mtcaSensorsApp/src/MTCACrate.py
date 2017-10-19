# File: MTCACrate.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: 
# Get sensor information for microTCA crate using ipmitool command.
#
# Changes:
# 2017-09-27 WL  Convert to Python3
# 2017-10-19 WL  Add TimeoutExpired execption handling

import math
import re
import time
import os
import sys
from devsup.db import IOScanListBlock

if os.name == 'posix' and sys.version_info[0] < 3:
    from subprocess32 import check_output
    from subprocess32 import CalledProcessError
    from subprocess32 import TimeoutExpired
else:
    from subprocess import check_output
    from subprocess import CalledProcessError
    from subprocess import TimeoutExpired

# Use this to suppress ipmitool/ipmiutil errors
#DEV_NULL = open(os.devnull, 'w')
# Use this to report ipmitool/ipmiutil errors
DEV_NULL = sys.stderr

SLOT_OFFSET = 96
PICMG_SLOT_OFFSET = 4
MCH_FRU_ID_OFFSET = 2

FW_TAG = "Product Extra"

HOT_SWAP_N_A = 0
HOT_SWAP_OK = 1
HOT_SWAP_FAULT = 2

HOT_SWAP_NORMAL_STS = ['lnc', 'ok']

COMMS_ERROR = 0
COMMS_OK = 1
COMMS_NONE = 2

COMMS_TIMEOUT = 5.0

MIN_GOOD_IPMI_MSG_LEN = 40

EPICS_ALARM_OFFSET = 0.001

BUS_IDS = {
    'pm': 10
    ,'cu': 30
    ,'amc': 193
    ,'mch': 194
}

SENSOR_NAMES = {
    '12 V PP': '12V0'
    ,'12V PP': '12V0'
    ,'12 V AMC': '12V0'
    ,'+12V PSU': '12V0'
    ,'+12V': '12V0'
    ,'PP': '12V0'
    ,'Base 12V': '12V0'
    ,'+12V_1': '12V0_1'
    ,'12VHH': '12V0_1'
    ,'+5V PSU': '5V0'
    ,'SMP': '5V0'
    ,'SMPP': '5V0_1'
    ,'3.3 V PP': '3V3'
    ,'3.3V MP': '3V3'
    ,'+3.3V PSU': '3V3'
    ,'+3.3V': '3V3'
    ,'MP': '3V3'
    ,'Base 3.3V': '3V3'
    ,'2.5 V': '2V5'
    ,'2.5V': '2V5'
    ,'Base 2.5V': '2V5'
    ,'1.8 V': '1V8'
    ,'1.8V': '1V8'
    ,'Base 1.8V': '1V8'
    ,'1.5V PSU': '1V5'
    ,'Base 1.5V': '1V5'
    ,'1.0V CORE': 'V_FPGA'
    ,'1.0 V': 'V_FPGA'
    ,'FPGA 1.2 V': 'V_FPGA'
    ,'Current 12 V': '12V0CURRENT'
    ,'Base Current': '12V0CURRENT'
    ,'Current 3.3 V': '3V3CURRENT'
    ,'Current 1.2 V': '1V2CURRENT'
    ,'Inlet': 'TEMP_INLET'
    ,'Temp 1 (inlet)': 'TEMP_INLET'
    ,'DC/DC Inlet': 'TEMP_INLET'
    ,'T PATH UPD': 'TEMP_INLET'
    ,'Outlet': 'TEMP_OUTLET'
    ,'Temp 2 (outlet)': 'TEMP_OUTLET'
    ,'FPGA S6': 'TEMP_OUTLET'
    ,'T DCDC UPD': 'TEMP_OUTLET'
    ,'FPGA DIE': 'TEMP_FPGA'
    ,'FPGA V5': 'TEMP_FPGA'
    ,'Middle': 'TEMP1'
    ,'FMC1': 'TEMP1'
    ,'Board Temp': 'TEMP1'
    ,'LM75 Temp': 'TEMP1'
    ,'T COOLER UPM': 'TEMP1'
    ,'Temp CPU': 'TEMP1'
    ,'FPGA PCB': 'TEMP2'
    ,'FMC2': 'TEMP2'
    ,'CPU Temp': 'TEMP2'
    ,'LM75 Temp2': 'TEMP2'
    ,'T TRAFO UPM': 'TEMP2'
    ,'Temp I/O': 'TEMP2'
    ,'CPLD': 'TEMP3'
    ,'Fan 1': 'FAN1'
    ,'Fan 2': 'FAN2'
    ,'Fan 3': 'FAN3'
    ,'Fan 4': 'FAN4'
    ,'Fan 5': 'FAN5'
    ,'Fan 6': 'FAN6'
    ,'Current(Sum)': 'I_TOTAL'
    ,'Ch01 Current': 'I01'
    ,'Ch02 Current': 'I02'
    ,'Ch03 Current': 'I03'
    ,'Ch04 Current': 'I04'
    ,'Ch05 Current': 'I05'
    ,'Ch06 Current': 'I06'
    ,'Ch07 Current': 'I07'
    ,'Ch08 Current': 'I08'
    ,'Ch09 Current': 'I09'
    ,'Ch10 Current': 'I10'
    ,'Ch11 Current': 'I11'
    ,'Ch12 Current': 'I12'
    ,'Ch13 Current': 'I13'
    ,'Ch14 Current': 'I14'
    ,'Ch15 Current': 'I15'
    ,'Ch16 Current': 'I16'
    ,'Ejector Handle': 'HOT_SWAP'
    ,'HotSwap': 'HOT_SWAP'
    ,'Hot Swap': 'HOT_SWAP'
}

DIGITAL_SENSORS = [
    'HOT_SWAP'
] 

ALARMS = {
    'Lower Critical': 'lolo'
    ,'Lower Non-Critical': 'low'
    ,'Upper Non-Critical': 'high'
    ,'Upper Critical': 'hihi'
}

EGU = { 
    'Volts': 'V'
    ,'Amps': 'A'
    ,'degrees C': 'C'
    ,'unspecified': ''
    ,'RPM': 'RPM'
}

ALARM_LEVELS = {
    'ok': 1
    ,'lnc': 2
    ,'unc': 2
    ,'lcr': 3
    ,'ucr': 3
    ,'lnr': 4
    ,'unr': 4
}

ALARM_STATES = [
    'UNSET'
    ,'NO_ALARM'
    ,'NON_CRITICAL'
    ,'CRITICAL'
    ,'NON_RECOVERABLE'
]

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

def create_ipmitool_command():
    """
    Creates common part of ipmitool command

    Args:
        None

    Returns:
        command (list): list of common command elements
    """

    # Get the path to ipmitool from the EPICS environment
    ipmitool_path = os.environ['IPMITOOL'] 
	
    # Create the IPMI tool command
    crate = get_crate()
    command = []
    command.append(os.path.join(ipmitool_path, "ipmitool"))
    command.append("-H")
    command.append(crate.host)
    command.append("-A")
    command.append("None")
    
    return command

def create_ipmiutil_command(ipmiutil_cmd):
    """
    Creates common part of ipmiutil command

    Args:
        ipmiutil_cmd (str): subcommand to pass to ipmiutil

    Returns:
        command (list): list of common command elements
    """

    # Create the IPMI util command
    crate = get_crate()
    command = []
    command.append("ipmiutil")
    command.append(ipmiutil_cmd)
    command.append("-N")
    command.append(crate.host)
    command.append("-U")
    command.append(crate.user)
    command.append("-P")
    command.append(crate.password)
    
    return command

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
        self.alarm_values_read = False
        self.alarms_valid = False

class FRU():
    """
    FRU information
    """

    def __init__(self, id = None, name = None, slot = None, bus = None, crate = None):
        """
        FRU class initializer

        Args:
            id (str): FRU ID (e.g., 193.101)
            name (str): card name
            slot(int): slot number
            bus(int): MTCA bus number
            crate(obj): reference to crate object

        Returns: 
            Nothing
        """
        self.id = id
        self.name = name
        self.slot  = slot
        self.bus  = bus
        self.crate = crate
        self.comms_ok = False
        self.alarm_level = ALARM_STATES.index('UNSET')

        # Dictionary for storing sensor values
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
        Read the sensors for this AMC Slot 

        Args:
            None

        Returns:
            Nothing
        """

        # Create the IPMI tool command
        command = create_ipmitool_command()
        command.append("sdr")
        command.append("entity")
        command.append(self.id)

        try:
            result = check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT).decode('utf-8')
            
            # Check if we got a good response from ipmitool
            # First test checks for an unplugged card
            # Second test checks for MCH comms failure
            if len(result) < MIN_GOOD_IPMI_MSG_LEN \
                or result.find('Error') >= 0:
                self.comms_ok = False
                max_alarm_level = ALARM_STATES.index('NON_RECOVERABLE')
            else:
                self.comms_ok = True
                max_alarm_level = ALARM_STATES.index('NO_ALARM')

                for line in result.splitlines():
                    try:
                        line_strip = [x.strip() for x in line.split('|')]
                        sensor_name, sensor_id, status, fru_id, val = line_strip

                        # Check if the sensor name is in the list of 
                        # sensors we know about
                        if sensor_name in SENSOR_NAMES.keys():
                            sensor_type = SENSOR_NAMES[sensor_name]
                            
                            if sensor_type in DIGITAL_SENSORS:
                                egu = ''
                                if sensor_type == 'HOT_SWAP':
                                    if status in HOT_SWAP_NORMAL_STS:
                                        value = HOT_SWAP_OK
                                    else:
                                        value = HOT_SWAP_FAULT
                            else:
                                # If this fails, it will trigger an exception,
                                # which we catch and allow to proceed
                                value, egu = val.split(' ', 1)

                            # Check if we have already created this sensor
                            if not sensor_type in self.sensors.keys():
                                self.sensors[sensor_type] = Sensor(sensor_name)
                        
                            sensor = self.sensors[sensor_type]

                            # Store the value
                            sensor.value = float(value)

                            # Get the simplified engineering units
                            if egu in EGU.keys():
                                sensor.egu = EGU[egu]
                            else:
                                sensor.egu = egu

                            # Set the alarm thresholds if we haven't already
                            if not sensor.alarm_values_read:
                                self.set_alarms(sensor_name)
                                sensor.alarm_values_read = True

                        # Do the card overall status evaluation
                        if sensor_name in SENSOR_NAMES.keys():

                            # Check the alarm status reported by the device
                            status = status.strip()
                            if status in ALARM_LEVELS.keys():
                                alarm_level = ALARM_LEVELS[status]
                                if alarm_level > max_alarm_level:
                                    # Special case to ignore normal state of Hot Swap sensor
                                    if sensor_name.strip() == 'Hot Swap' and status == 'lnc':
                                        pass
                                    else:
                                        max_alarm_level = alarm_level

                    except ValueError as e:
                        print("Caught ValueError: {}".format(e))
                        pass

            self.alarm_level = max_alarm_level

        except TimeoutExpired as e:
            print("read_sensors: Caught TimeoutExpired exception: {}".format(e))
            self.comms_ok = False


    def set_alarms(self, name):
        """
        Function to set alarm setpoints in AI records

        Args:
            name: sensor name

        Returns:
            Nothing
        """
        command = create_ipmitool_command()
        command.append("sensor")
        command.append("get")
        command.append(name)

        try:
            result = check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT).decode('utf-8')
            for line in result.splitlines():
                try:
                    description, value = [x.strip() for x in line.split(':',1)]
                    if description in ALARMS.keys():
                        sensor_type = SENSOR_NAMES[name]
                        setattr(self.sensors[sensor_type], ALARMS[description], float(value))
                        self.sensors[sensor_type].alarms_valid = True       
                except ValueError:
                    pass
        except CalledProcessError as e:
            # This traps any errors thrown by the call to ipmitool. 
            # This occurs if all alarm thresholds are not set. 
            # See Jira issue DIAG-23
            # https://jira.frib.msu.edu/projects/DIAG/issues/DIAG-23
            #print ("Caught subprocess.CalledProcessError: {}".format(e))
            # Be silent
            pass
        except TimeoutExpired as e:
            print("set_alarms: Caught TimeoutExpired exception: {}".format(e))

    def reset(self):
        """
        Function to reset AMC card

        Args:
            name: sensor name

        Returns:
            Nothing
        """

        # Deactivate the card
        command = create_ipmitool_command()
        command.append("picmg")
        command.append("deactivate")
        command.append(str(self.slot + PICMG_SLOT_OFFSET))

        try:
            result = check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT)
        except TimeoutExpired as e:
            print("reset: Caught TimeoutExpired exception: {}".format(e))
        
        # TODO: Add a resetting status here to allow other reads to wait
        # See DIAG-68.

        # Wait for the card to shut down
        time.sleep(2.0)

        # Activate the card
        command = create_ipmitool_command()
        command.append("picmg")
        command.append("activate")
        command.append(str(self.slot + PICMG_SLOT_OFFSET))

        try:
            result = check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT)
        except TimeoutExpired as e:
            print("reset: Caught TimeoutExpired exception: {}".format(e))

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

        # Initialize dictionaries of FRUs
        self.frus = {}
        self.frus_inited = False

        # Initialize dictionaries for MCH firmware
        self.mch_fw_ver = {}
        self.mch_fw_date = {}

        # Create scan list for I/O Intr records
        self.scan_list = IOScanListBlock()

    def populate_fru_list(self):
        """ 
        Call MCH and get list of AMC slots

        Args:   
            None

        Returns:
            Nothing
        """

        # Clear the list each time this runs. Allows a user-requested
        # refresh of the list.
        self.frus_inited = False
        self.frus = {}

        if self.host != None and self.user != None and self.password != None:
            command = create_ipmitool_command()
            command.append("sdr")
            command.append("elist")
            command.append("fru")

            try:
                result = check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT)
            except TimeoutExpired as e:
                print("populate_fru_list: Caught TimeoutExpired exception: {}".format(e))
            
            for line in result.splitlines():
                try:
                    name, ref, status, id, desc = line.split('|')
                    
                    # Get the AMC slot number
                    bus, slot = id.strip().split('.')
                    bus, slot = int(bus), int(slot)
                    
                    slot -= SLOT_OFFSET
                    if (bus, slot) not in self.frus.keys():
                        self.frus[(bus, slot)] = FRU(
                                name = name.strip(), 
                                id = id.strip(), 
                                slot = slot, 
                                bus = bus,
                                crate = self)
                except ValueError:
                    print ("Couldn't parse {}".format(line))
            self.frus_inited = True
        else:
            print("Crate information not populated")

        # Get the MCH firmware info
        self.read_fw_version()

    def read_sensors(self):
        """ 
        Call read all sensor values

        Args:   
            None

        Returns:
            Nothing
        """

        if self.frus_inited:
            for fru in self.frus:
                self.frus[fru].read_sensors()   

    def read_fw_version(self):
        """ 
        Get MCH firmware version

        Args:   
            None

        Returns:
            Nothing
        """
        
        # This function expects the firmware version to be in a line
        # prefixed with 'Product Extra'.
        # At the moment, it takes the form:
        # Product Extra         : MCH FW V2.18.8 Final (r14042) (Mar 31 2017 - 11:29)
        # The following two parts will be extracted:
        # mch_fw_ver: V2.18.8 Final
        # mch_fw_date: Mar 31 2017 - 11:29
        # If NAT change the format, then this function will need to be updated

        pattern = ".*: MCH FW (.*) \(.*\) \((.*)\)"

        for mch in range(1,3):
            # Create the command
            command = create_ipmitool_command()
            command.append("fru")
            command.append("print")
            command.append(str(mch + MCH_FRU_ID_OFFSET))

            try:
                result = check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT).decode('utf-8')

                for line in result.splitlines():
                    if FW_TAG in line:
                        match = re.match(pattern, line)
                        if match:
                            self.mch_fw_ver[mch] = match.group(1)
                            self.mch_fw_date[mch] = match.group(2)
                        else:
                            self.mch_fw_ver[mch] = "Unknown"
                            self.mch_fw_date[mch] = "Unknown"
            except CalledProcessError as e:
                        self.mch_fw_ver[mch] = "Unknown"
                        self.mch_fw_date[mch] = "Unknown"
            except TimeoutExpired as e:
                print("read_fw_version: Caught TimeoutExpired exception: {}".format(e))

    def reset(self):
        """
        Reset crate using ipmitool command

        Args:
            None

        Returns:
            Nothing
        """

        # Assemble the crate reset command
        command = create_ipmitool_command()
        command.append("raw")
        command.append("0x06")
        command.append("0x03")

        # Issue the reset command
        try:
            check_output(command, stderr=DEV_NULL, timeout=COMMS_TIMEOUT)
        except CalledProcessError:
            pass
        except TimeoutExpired as e:
            print("reset: Caught TimeoutExpired exception: {}".format(e))

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
                bus (str, optional): mtca bus type (see BUS_IDS) 
                slot (int, optional): amc slot number 
                sensor(str, optional): sensor to read

        Returns:
            Nothing
        """

        args_list = args.split(None, 3)
        if len(args_list) == 4:
            fn, bus, slot, sensor = args_list
        elif len(args_list) == 3:
            fn, bus, slot = args_list
            sensor = None
        elif len(args_list) == 2:
            fn, slot = args_list
            bus = 0
            sensor = None
        else:
            fn = args
            bus = 0
            slot = 0
            sensor = None

        self.crate = get_crate()
        # Set up the function to be called when the record processes
        self.process = getattr(self, fn)
        # Allow for I/O Intr scanning
        self.allowScan = self.crate.scan_list.add
        self.slot = int(slot)
        if bus in BUS_IDS.keys():
            self.bus = BUS_IDS[bus]
        else:
            self.bus = None
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
        if self.crate.frus_inited:
            try:
                self.crate.read_sensors()
                self.crate.scan_list.interrupt()
            except AttributeError as e:
                # TODO: Work out why we get this exception
                print ("Caught AttributeError: {}".format(e))


    def get_val(self, rec, report):
        """ 
        Get sensor reading

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        valid_sensor = False

        # Check if we have a valid sensor and slot number
        if self.sensor != None and not math.isnan(self.slot):
            index = (self.bus, self.slot)
            if index in self.crate.frus.keys():
                # Check if this is a valid sensor
                if self.sensor in self.crate.frus[index].sensors.keys():
                    if not self.alarms_set:
                        self.set_alarms(rec)
                    card = self.crate.frus[index]
                    sensor = card.sensors[self.sensor]
                    val = sensor.value
                    egu = sensor.egu
                    desc = sensor.name
                    type = SENSOR_NAMES[desc]
                    rec.VAL = val
                    rec.EGU = egu
                    rec.DESC = desc

                    # Check if we are still communication with the card
                    if card.comms_ok:
                        rec.UDF = 0
                    else:
                        rec.UDF = 1

                    valid_sensor = True
        if not valid_sensor:
            rec.VAL = float('NaN')
            rec.UDF = 0

    def set_alarms(self, rec):
        """
        Set alarm values in PV

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        sensor = self.crate.frus[(self.bus, self.slot)].sensors[self.sensor]
        sensor_type = SENSOR_NAMES[sensor.name]
        try:
            rec.LOLO = sensor.lolo - EPICS_ALARM_OFFSET
            rec.LOW = sensor.low - EPICS_ALARM_OFFSET
            rec.HIGH = sensor.high + EPICS_ALARM_OFFSET
            rec.HIHI = sensor.hihi + EPICS_ALARM_OFFSET

            if sensor.alarms_valid:
                rec.LLSV = 2 # MAJOR
                rec.LSV = 1 # MINOR
                rec.HSV = 1 # MINOR
                rec.HHSV = 2 # MAJOR
            else:
                rec.LLSV = 0 # NO_ALARM
                rec.LSV = 0 # NO_ALARM
                rec.HSV = 0 # NO_ALARM
                rec.HHSV = 0 # NO_ALARM

            self.alarms_set = True
        except KeyError as e:
            print ("Caught KeyError: {}".format(e))

    def get_name(self, rec, report):
        """
        Get card name

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        # Check if this card exists
        if not math.isnan(self.slot) and \
        (self.bus, self.slot) in self.crate.frus.keys():
            rec.VAL = self.crate.frus[(self.bus, self.slot)].name
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
        if (self.bus, self.slot) in self.crate.frus.keys():
            rec.VAL = self.crate.frus[(self.bus, self.slot)].slot
        else:
            rec.VAL = float('NaN')
        # Make the record defined regardless of value
        rec.UDF = 0

    def get_status(self, rec, report):
        """
        Get card alarm status

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        # Check if this card exists
        if (self.bus, self.slot) in self.crate.frus.keys():
            rec.VAL = self.crate.frus[(self.bus, self.slot)].alarm_level
        else:
            rec.VAL = ALARM_STATES.index('UNSET')
        # Make the record defined regardless of value
        rec.UDF = 0

    def get_comms_sts(self, rec, report):
        """
        Get FRU communications status

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        # Check if the card exists
        if (self.bus, self.slot) in self.crate.frus.keys():
            if self.crate.frus[(self.bus, self.slot)].comms_ok:
                rec.VAL = COMMS_OK
            else:
                rec.VAL = COMMS_ERROR
        else:
            # Set the comms error given that the slot is empty
            rec.VAL = COMMS_NONE

        # Make the record defined regardless of value
        rec.UDF = 0

    def get_fw_ver(self, rec, report):
        """
        Get MCH firmware version

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        rec.VAL = self.crate.mch_fw_ver[self.slot]

    def get_fw_date(self, rec, report):
        """
        Get MCH firmware date

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        rec.VAL = self.crate.mch_fw_date[self.slot]

    def reset(self, rec, report):
        """
        Reset AMC card

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """

        # Check if the card exists
        if (self.bus, self.slot) in self.crate.frus.keys():
            self.crate.frus[(self.bus, self.slot)].reset()

    def crate_reset(self, rec, report):
        """ 
        Power cycle crate

        Args:
            None

        Returns:
            Nothing
        """

        self.crate.reset()

build = MTCACrateReader

