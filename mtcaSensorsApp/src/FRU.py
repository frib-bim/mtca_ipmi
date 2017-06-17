#!/usr/bin/env python
# File: FRU.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get sensor information for FRU
# FRU = Field Replaceable Unit
#

from devsup.db import IOScanListBlock
#from devsup.util import StoppableThread
from subprocess import check_output
import threading
import time
import os
import MTCACrate

_frus = {}

def get_fru(id):
    """
    Find existing crate object, or create new one.

    Args:
        id: FRU ID

    Returns: 
        FRUScanner object
    """
    try:
        return _frus[id]
    except KeyError:
        fru = FRUScanner(id)
        _frus[id] = fru
        return fru

class Sensor():
    """
    Sensor information
    """

    def __init__(self, name=None):
        """
        Sensor class initializer

        Args:
            name (str): Sensor name

        Returns: 
            Nothing
        """
        self.name = name
        self.value = None
        self.egu = None
        self.status = None
        self.sensor_id = None
        self.fru_id = None
        self.lolo = 0.0
        self.low = 0.0
        self.high = 0.0
        self.hihi = 0.0
        self.alarms_set = False

    def __str__(self):
        """
        Sensor class printout
        
        Args:
            None

        Returns:
            String representation of FRU
        """
        return "Name: {}, Value: {}".format(self.name, self.value)

class FRUScanner():
    """
    Class for getting sensor information for a FRU 
    """
    
    def __init__(self, id):
        """
        Initializer for FRUScanner object.

        Args:
            id: FRU ID

        Returns:
            Nothing
        """

        self.id = id
        self.host = None
        self.user = None
        self.password = None

        self.scan_list = IOScanListBlock()
        
        # Initialize list of FRUs
        self.sensors = {}

        self.attr_dict = {
            'Lower Critical': 'lolo',
            'Lower Non-Critical': 'low',
            'Upper Non-Critical': 'high',
            'Upper Critical': 'hihi'
            }
        
    def read_sensors(self, crate):
        """ 
        Call MCH and get sensors for this FRU

        Args:   
            None

        Returns:
            Nothing
        """

        if crate.host != None and crate.user != None and crate.password != None:
            command = []
            command.append("ipmitool")
            command.append("-H")
            command.append(crate.host)
            command.append("-U")
            command.append(crate.user)
            command.append("-P")
            command.append(crate.password)
            command.append("sdr")
            command.append("entity")
            command.append(self.id)

            result = check_output(command)
            
            for line in result.splitlines():
                try:
                    line_strip = [x.strip() for x in line.split('|')]
                    name, sensor_id, status, fru_id, val = line_strip
                    value, egu = val.split(' ', 1)
                    if name in self.sensors.keys():
                        self.sensors[name].value = float(value)
                        self.sensors[name].status = status
                    else:
                        self.sensors[name] = Sensor(name)
                        self.sensors[name].sensor_id = sensor_id
                        self.sensors[name].fru_id = fru_id
                        self.sensors[name].value = float(value)
                        self.sensors[name].egu = egu
                        self.sensors[name].status = status
                        if not self.sensors[name].alarms_set:
                            self.set_alarms(crate, name)

                except ValueError:
                    pass

            #for key in self.sensors:
                #print(self.sensors[key])

    def set_alarms(self, crate, name):
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
        command.append(crate.host)
        command.append("-U")
        command.append(crate.user)
        command.append("-P")
        command.append(crate.password)
        command.append("sensor")
        command.append("get")
        command.append(name)

        result = check_output(command)

        for line in result.splitlines():
            try:
                item, value = [x.strip() for x in line.split(':',1)]
                if item in self.attr_dict.keys():
                    setattr(self.sensors[name], self.attr_dict[item], float(value))
            except ValueError:
                pass

        self.sensors[name].alarms_set = True       

class FRUReader:
    """
    Main class for reading FRU sensor values from EPICS
    """
    raw = True

    def __init__(self, rec, args):
        """
        Initializer function

        Args:
            rec: pyDevSup record object
            args: arguments from the EPICS record INP field, consisting of
                fn: function to be called for this record
                fru_id: e.g., 192.101
                sensor_name: e.g., Current 1.2 V
    
        Returns:
            Nothing
        """

        # Set up the crate info
        self.crate = MTCACrate.get_crate()

        # Get the information about the sensor
        args_list = args.split(None,2)
        if len(args_list) == 3:
            fn, fru_id, sensor_name = args_list
        else:
            fn, fru_id = args_list
            sensor_name = None

        self.fru_id = fru_id
        self.sensor_name = sensor_name
        self.egu_set = False
        self.alarms_set = False
        self.fru = get_fru(fru_id)
    
        self.process = getattr(self, fn)
        self.allowScan = self.fru.scan_list.add

        try:
            rec.UDF = 0
        except AttributeError:
            pass

    def detach(self, rec):
        pass

    def get_val(self, rec, report):
        """ 
        Get a sensor value and store in the PV

        Args:
            rec: database record 
            report: ?

        Returns: 
            Nothing
        """
        rec.VAL = self.fru.sensors[self.sensor_name].value

        if not self.egu_set:
            rec.EGU = self.fru.sensors[self.sensor_name].egu
            self.egu_set = True

        if (not self.alarms_set) and self.fru.sensors[self.sensor_name].alarms_set:
            rec.LOLO = self.fru.sensors[self.sensor_name].lolo
            rec.LOW = self.fru.sensors[self.sensor_name].low
            rec.HIGH = self.fru.sensors[self.sensor_name].high
            rec.HIHI = self.fru.sensors[self.sensor_name].hihi
            rec.LLSV = 2 # MAJOR
            rec.LSV = 1 # MINOR
            rec.HSV = 1 # MINOR
            rec.HHSV = 2 # MAJOR
            self.alarms_set = True

    def update(self, rec, report):
        """
        Call this function to update the sensor values

        Args:
            rec: database record 
            report: ?

        Returns: 
            Nothing
        """
        self.fru.read_sensors(self.crate)
        self.fru.scan_list.interrupt()

build = FRUReader
