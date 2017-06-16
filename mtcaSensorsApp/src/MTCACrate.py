#!/usr/bin/env python
# File: MTCACrate.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get FRU information for microTCA crate.
# FRU = Field Replaceable Unit
#

#from devsup.db import IOScanListBlock
#from devsup.util import StoppableThread
import threading
from subprocess import check_output

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

        Returns: 
            Nothing
        """
        self.id = id
        self.name = name

    def __str__(self):
        """
        FRU class printout
        
        Args:
            None

        Returns:
            String representation of FRU
        """
        return "ID: {}, Name: {}".format(self.id, self.name)


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

        # Initialize list of FRUs
        self.frus = []

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
                    self.frus.append(FRU(name=name.strip(), id=id.strip()))
                except ValueError:
                    print "Couldn't parse {}".format(line)
        else:
            print("Crate information not populated")

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
            args: arguments from EPICS record
                fn: function to be called

        Returns:
            Nothing
        """

        fn = args
	self.crate = get_crate()
        self.process = getattr(self, fn)

        try:
            rec.UDF = 0
        except AttributeError:
            pass

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

    def set_user(self, rec, report):
        """
        Set user name

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.user = rec.VAL

    def set_password(self, rec, report):
        """
        Set password 

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.password = rec.VAL

    def get_fru_list(self, rec, report):
        """
        Get FRU info from crate

        Args:
            rec: pyDevSup record object

        Returns:
            Nothing
        """
        self.crate.populate_fru_list()

build = MTCACrateReader

