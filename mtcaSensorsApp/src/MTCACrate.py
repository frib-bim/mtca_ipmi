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
# 2017-12-22 WL  Add card rescan after crate reset
# 2017-12-26 WL  Create utility function for calling ipmitool
# 2017-12-27 WL  Convert to ipmitool shell

import math
import re
import time
import datetime
import os
import sys
import threading
from devsup.db import IOScanListBlock
from devsup.hooks import addHook

if os.name == 'posix' and sys.version_info[0] < 3:
    import subproces32 as subprocess
    from subprocess32 import check_output
    from subprocess32 import CalledProcessError
    from subprocess32 import TimeoutExpired
    import Queue 
else:
    import subprocess 
    from subprocess import check_output
    from subprocess import CalledProcessError
    from subprocess import TimeoutExpired
    import queue as Queue

# Use this to suppress ipmitool/ipmiutil errors
ERR_FILE = open(os.devnull, 'w')
# Use this to report ipmitool/ipmiutil errors
#ERR_FILE = sys.stderr

SLOT_OFFSET = 96
PICMG_SLOT_OFFSET = 4
MCH_FRU_ID_OFFSET = 2

FW_TAG = "Product Extra"

HOT_SWAP_N_A = 0
HOT_SWAP_OK = 1
HOT_SWAP_FAULT = 2

HOT_SWAP_NORMAL_STS = ['lnc', 'ok']
HOT_SWAP_NO_VALUE_NORMAL_STS = 'lnc'
HOT_SWAP_NORMAL_VALUE = [
        'Module Handle Closed'
       , 'Device Absent']
HOT_SWAP_FAULT_VALUE = ['Quiesced']

COMMS_ERROR = 0
COMMS_OK = 1
COMMS_NONE = 2

COMMS_TIMEOUT = 5.0

MIN_GOOD_IPMI_MSG_LEN = 40

EPICS_ALARM_OFFSET = 0.001
NO_ALARM_OFFSET = 0.01

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

FAN_ALARMS = {
    'lolo': 500
    ,'low': 1000
    ,'high': 3500
    ,'hihi': 4000
}

MCH_START_TIME = datetime.datetime(1970,1,1,0,0,0)

IPMITOOL_SHELL_PROMPT = 'ipmitool>'
QUEUE_THREAD_SLEEP_TIME = 0.0005

def get_crate():
    """
    Find existing crate object, or create new one.

    Args:
        None

    Returns: 
        MTCACrate object
    """
    
    try:
        return _crate
    except:
        pass

# Cleanup on IOC exit
def stop():
    """
    Cleanup on IOC exit
    """
    
    crate = get_crate()
    # Tell the thread to stop
    crate.mch_comms.stop = True
    # Stop the ipmitool shell process
    crate.mch_comms.ipmitool_shell.terminate()
    crate.mch_comms.ipmitool_shell.kill()

addHook('AtIocExit', stop)

class MCH_comms():
    """ 
    Class to handle all comms to MCH
    """

    def __init__(self, _crate):
        self.ipmitool_shell = None
        self.ipmitool_out_queue = None
        self.crate = _crate
        self.connected = False
        self.stop = False
        self.comms_lock = threading.Lock()

    def enqueue_output(self, out, queue):
        """
        Helper function for queuing piped output from ipmitool shell

        Args:
            out (pipe): pipe to listen to
            queue (queue): output queue for results

        Returns:
            Nothing
        """

        started = False
        finished = False

        while not self.stop:
            line = out.readline()
            queue.put(line)
            # Test if we have reached the end of the output
            if started and IPMITOOL_SHELL_PROMPT in line.decode('ascii'):
                finished = True
            if IPMITOOL_SHELL_PROMPT in line.decode('ascii'):
                started = True
            if finished and self.comms_lock.locked():
                self.comms_lock.release()
                started = False
                finished = False

            time.sleep(QUEUE_THREAD_SLEEP_TIME)
        return

    def create_ipmitool_command(self):
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
        #crate = get_crate()
        command = []
        command.append(os.path.join(ipmitool_path, "ipmitool"))
        command.append("-H")
        command.append(self.crate.host)
        command.append("-A")
        command.append("None")
        
        return command

    def ipmitool_shell_connect(self):
        """
        Connect to the ipmitool shell

        Args: 
            None
        Returns:
            Nothing
        """

        if not self.connected:
            command = self.create_ipmitool_command()
            command.append("shell")

            self.ipmitool_shell = subprocess.Popen(
                    command, 
                    stdin=subprocess.PIPE, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)

            # Set up the queue and thread to monitor the stdout pipe
            q = Queue.Queue()

            self.t = threading.Thread(
                    target=self.enqueue_output, 
                    args=(self.ipmitool_shell.stdout, q))
            self.t.start()
            self.ipmitool_out_queue = q
            self.connected = True

    def call_ipmitool_command(self, ipmitool_cmd):
        """
        Generate and call ipmitool command using ipmitool shell connection

        Args:
            ipmitool_cmd: command string

        Returns:
            result (string): response of ipmitool to command
        """

        command = ' '.join(str(e) for e in ipmitool_cmd)
        command += '\n'
        
        result_list = []

        #with (yield from self.comms_lock):
        if not self.comms_lock.locked():
            self.comms_lock.acquire()
            self.ipmitool_shell_connect()
            self.ipmitool_shell.stdin.write(command.encode('ascii'))
            self.ipmitool_shell.stdin.flush()
            # Write a null command to get an 'ipmitool>' response
            # that indicates the end of the data transmission
            self.ipmitool_shell.stdin.write('\n'.encode('ascii'))
            self.ipmitool_shell.stdin.flush()
        
            # Wait until the thread releases the lock after all data has been received
            while self.comms_lock.locked():
                time.sleep(0.1)

            # Wait for some data in the result queue
            #while self.ipmitool_out_queue.empty():
                #time.sleep(0.1)
            
            # pull the data out of the queue
            while not self.ipmitool_out_queue.empty():
                line = self.ipmitool_out_queue.get_nowait()
                result_list.append(line.decode('ascii'))

            # once we are here, we can release the lock
            #self.comms_lock.release()

        # Drop the first value, as it is an echo of the command
        return "".join(result_list[1:])

    def call_ipmitool_direct_command(self, ipmitool_cmd):
        """
        Generate and call ipmitool command bypassing the shell

        Args:
            ipmitool_cmd: command string

        Returns:
            result (string): response of ipmitool to command
        """

        command = self.create_ipmitool_command()
        command.extend(ipmitool_cmd)
        
        return subprocess.check_output(command, timeout = COMMS_TIMEOUT)

    def get_ipmitool_version(self):
            # Print ipmitool information
            ipmitool_path = os.environ['IPMITOOL']
            command = []
            command.append(os.path.join(ipmitool_path, "ipmitool"))
            command.append("-V")

            return check_output(
                    command, 
                    stderr=ERR_FILE, 
                    timeout=COMMS_TIMEOUT).decode('ascii')


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
        self.valid = False

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
        self.mch_comms = self.crate.mch_comms
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

        if self.crate.crate_resetting == False:
            try:
                result = self.mch_comms.call_ipmitool_command(["sdr", "entity", self.id])
                
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
                            if not IPMITOOL_SHELL_PROMPT in line:
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
                                                if status == HOT_SWAP_NO_VALUE_NORMAL_STS:
                                                    value = HOT_SWAP_OK
                                                else:
                                                    if val in HOT_SWAP_NORMAL_VALUE:
                                                        value = HOT_SWAP_OK
                                                    else:
                                                        value = HOT_SWAP_FAULT
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
                                    sensor.valid = True

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
                                            if (sensor_name.strip() == 'Hot Swap' 
                                                    and status == 'lnc'):
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

    def set_sensors_invalid(self):
        """
        Set the status of sensors for this AMC Slot to invalid

        Args:
            None

        Returns:
            Nothing
        """

        for sensor_name in self.sensors.keys():
            self.sensors[sensor_name].valid = False 

    def set_alarms(self, name):
        """
        Function to set alarm setpoints in AI records

        Args:
            name: sensor name

        Returns:
            Nothing
        """
        # Special treatment for fan sensors
        if "Fan" in name:
            for alarm_level in FAN_ALARMS.keys():
                sensor_type = SENSOR_NAMES[name]
                setattr(self.sensors[sensor_type], alarm_level, FAN_ALARMS[alarm_level])
                self.sensors[sensor_type].alarms_valid = True       
        # All other sensors
        else:
            result = ""
            try:
                result = self.mch_comms.call_ipmitool_command(["sensor", "get", '"'+name+'"'])
            except CalledProcessError as e:
                # This traps any errors thrown by the call to ipmitool. 
                # This occurs if all alarm thresholds are not set. 
                # See Jira issue DIAG-23
                # https://jira.frib.msu.edu/projects/DIAG/issues/DIAG-23
                # Be silent
                print("set_alarms: Caught CalledProcessError exception: {}".format(e))
                pass
            except TimeoutExpired as e:
                print("set_alarms: Caught TimeoutExpired exception: {}".format(e))

            for line in result.splitlines():
                try:
                    description, value = [x.strip() for x in line.split(':',1)]
                    if description in ALARMS.keys():
                        sensor_type = SENSOR_NAMES[name]
                        setattr(self.sensors[sensor_type], ALARMS[description], float(value))
                        self.sensors[sensor_type].alarms_valid = True       
                except ValueError as e:
                    # Traps lines that cannot be split. Be silent.
                    pass

    def reset(self):
        """
        Function to reset AMC card

        Args:
            name: sensor name

        Returns:
            Nothing
        """

        # Deactivate the card
        try:
            result = self.mch_comms.call_ipmitool_command(["picmg", "deactivate", (str(self.slot + PICMG_SLOT_OFFSET))])
        except CalledProcessError:
            pass
        except TimeoutExpired as e:
            print("reset: Caught TimeoutExpired exception: {}".format(e))
        
        # TODO: Add a resetting status here to allow other reads to wait
        # See DIAG-68.

        # Wait for the card to shut down
        time.sleep(2.0)

        # Activate the card
        try:
            result = self.mch_comms.call_ipmitool_command(["picmg", "activate", str(self.slot + PICMG_SLOT_OFFSET)])
        except CalledProcessError:
            pass
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

        # Store IOC process start time
        self.ioc_start_time = datetime.datetime.now()

        # Create scan list for I/O Intr records
        self.scan_list = IOScanListBlock()

        # Flag to indicate whether crate is being reset
        self.crate_resetting = False

        # Create link for all comms
        self.mch_comms = MCH_comms(self)

        try:
            result = self.mch_comms.get_ipmitool_version()
            #result = check_output(command, stderr=ERR_FILE, timeout=COMMS_TIMEOUT).decode('utf-8')
            print(result)
            
            ipmitool_path = os.environ['IPMITOOL'] 
            print("ipmitool path = {}".format(ipmitool_path))
        except CalledProcessError:
            pass
        except TimeoutExpired as e:
            print("MTCACrate::__init__: Caught TimeoutExpired exception: {}".format(e))

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

        result = ""

        if (self.host != None 
                and self.user != None 
                and self.password != None 
                and self.crate_resetting == False):

            # Need to repeat this until we get a proper reponse to the FRU list
            while len(result) <= 0:
                try:
                    result = self.mch_comms.call_ipmitool_command(["sdr", "elist", "fru"])
                except CalledProcessError:
                    pass
                except TimeoutExpired as e:
                    print("populate_fru_list: Caught TimeoutExpired exception: {}".format(e))
                
                # Wait a short whlie before trying again
                time.sleep(1.0)

            for line in result.splitlines():
                try:
                    if not IPMITOOL_SHELL_PROMPT in line:
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
        else:
            for fru in self.frus:
                self.frus[fru].set_sensors_invalid()   

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
            try:
                result = self.mch_comms.call_ipmitool_command(["fru", "print", str(mch + MCH_FRU_ID_OFFSET)])

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

    def read_mch_uptime(self):
        """ 
        Get MCH uptime

        Args: 
            None

        Returns:
            Nothing
        """

        # Read the current MCH time
        if self.crate_resetting == False:
            try:
                result = self.mch_comms.call_ipmitool_command(["sel", "time", "get"])

                # Check that the result is the expected format
                if re.match('\d\d\/\d\d\/\d\d\d\d \d\d:\d\d:\d\d', result.splitlines()[0].strip()):
                    mch_now = datetime.datetime.strptime(result.splitlines()[0].strip(), '%m/%d/%Y %H:%M:%S')

                    # Calculate the uptime
                    mch_uptime_diff = mch_now - MCH_START_TIME

                    self.mch_uptime = (
                            mch_uptime_diff.days + 
                            mch_uptime_diff.seconds/(24*60*60))

            except CalledProcessError:
                pass
            except TimeoutExpired as e:
                print("read_mch_uptime: Caught TimeoutExpired exception: {}".format(e))

    def reset(self):
        """
        Reset crate using ipmitool command

        Args:
            None

        Returns:
            Nothing
        """

        # Issue the reset command
        try:
            self.crate_resetting = True
            # Reset the FRU init status to stop attempts to read the sensors
            self.frus_inited = False
            # Wait a few seconds to allow any existing ipmitool requests to complete
            print("Short wait before resetting (2 s)")
            time.sleep(2.0)
            # Force the records to invalid
            print("Force sensor read to set invalid")
            self.read_sensors()
            print("Triggering records to scan")
            self.scan_list.interrupt()
            # Reset the crate
            print("Resetting crate now")
            self.mch_comms.call_ipmitool_command(["raw", "0x06", "0x03"])
            # Stop the ipmitool session. System will reconnect on restart
            print("Stopping ipmitool shell process")
            self.mch_comms.ipmitool_shell.terminate()
            time.sleep(2.0)
            self.mch_comms.ipmitool_shell.kill()
            self.mch_comms.ipmitool_shell = None
            self.mch_comms.connected = False
            
            # Stop the reader thread
            self.mch_comms.stop = True
            # Wait for the thread to stop
            self.mch_comms.t.join()
            self.mch_comms.t = None
            # Allow the thread to restart
            self.mch_comms.stop = False


        except CalledProcessError:
            pass
        except TimeoutExpired as e:
            # Be silent. We expect this command to timeout.
            pass

        # Wait for the crate to come back up, and then rescan the card list
        crate_up = False
        retries = 0
        MAX_RETRIES = 10

        # Wait for the crate to come back up
        print("Waiting for MCH to come up")
        #time.sleep(60.0)
        while not crate_up and retries < MAX_RETRIES:
            try:
                print ("Checking comms to MCH, attempt number {}".format(retries+1))
                result = self.mch_comms.call_ipmitool_direct_command(["mc", "info"])
                # If we don't throw an exception, assume the crate is up
                crate_up = True
                self.crate_resetting = False
                # Wait a few seconds. This needs to be 15 s to allow the MCH
                # to populate its sensor lists.
                print("MCH is up")
                print("Short wait (15 s) to allow MCH to update sensor list")
                time.sleep(15.0)
                # Restart the communications
                print("Restarting comms to MCH")
                result = self.mch_comms.call_ipmitool_command(["mc", "info"])

                # Reread the card list
                print("Updating card and sensor list")
                self.populate_fru_list()
                print("Lists updated.")
                print("Reading data values again, this will take a few seconds")
            except CalledProcessError as e:
                retries+=1
            except TimeoutExpired as e:
                # OK to get timeout exceptions here. Be silent.
                retries+=1

        if retries >= MAX_RETRIES:
            # Reset this to allow other comms, even though they may fail
            self.crate_resetting = False
            print ("Reached maximum number of retries. Please try resetting crate again.")

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
                self.crate.read_mch_uptime()
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
                    if sensor.valid and card.comms_ok:
                        rec.UDF = 0
                    else:
                        rec.UDF = 1
                        #rec.VAL = float('NaN')
                        #rec.VAL = 0.0
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
            # Handle sensors that do not get non-critical alarms
            if sensor.low == 0 and sensor.lolo != 0:
                sensor.low = sensor.lolo + NO_ALARM_OFFSET
            if sensor.high == 0 and sensor.hihi != 0:
                sensor.high = sensor.hihi - NO_ALARM_OFFSET

            # Set the EPICS PV alarms, with small offset to allow for different
            # alarm behaviour
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
            if self.crate.frus[(self.bus, self.slot)].comms_ok and not self.crate.crate_resetting:
                rec.VAL = COMMS_OK
            else:
                rec.VAL = COMMS_ERROR
        else:
            # Set the comms status given that the slot is empty
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

    def get_uptime(self, rec, report):
        """
        Get MCH uptime 

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        rec.VAL = self.crate.mch_uptime
        rec.UDF = 0

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

