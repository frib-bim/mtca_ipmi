#!/usr/bin/env python
# File: FRU.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get sensor information for FRU
# FRU = Field Replaceable Unit
#
# Assumes the following environment variables are set:
# MTCA_HOST
# MTCA_USER
# MTCA_PASSWORD

from devsup.db import IOScanListBlock
#from devsup.util import StoppableThread
from subprocess import check_output
import threading
import time
import os


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

class MTCACrate():
	"""
	Class to hold crate information
	"""

	def __init__(self):
		""" 
		Crate class initializer
		"""

		self.host = None
		self.user = None
		self.password = None

_crate = MTCACrate()

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

	def __str__(self):
		"""
		Sensor class printout
		
		Args:
			None

		Returns:
			String representation of FRU
		"""
		return "Name: {}, Value: {}".format(self.name, self.value)

#class FRUScanner(StoppableThread)
# TODO: work out if this should be a thread or just processed from EPICS

class FRUScanner(threading.Thread):
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
		
		super(FRUScanner, self).__init__()
		
		# Initialize list of FRUs
		self.sensors = {}

		self.should_run = True

	def read_sensors(self):
		""" 
		Call MCH and get sensors for this FRU

		Args:	
			None

		Returns:
			Nothing
		"""

		command = []
		command.append("ipmitool")
		command.append("-H")
		command.append(self.host)
		command.append("-U")
		command.append(self.user)
		command.append("-P")
		command.append(self.password)
		command.append("sdr")
		command.append("entity")
		command.append(self.id)

		result = check_output(command)
		
		for line in result.splitlines():
			try:
				name, sensor_id, status, fru_id, val = line.split('|')
				value, egu = val.strip().split(' ', 1)
				if name in self.sensors.keys():
					self.sensors[name].value = value
					self.sensors[name].status = status
				else:
					self.sensors[name] = Sensor(name)
					self.sensors[name].sensor_id = sensor_id
					self.sensors[name].fru_id = fru_id
					self.sensors[name].value = value
					self.sensors[name].egu = egu
					self.sensors[name].status = status
			except ValueError:
				pass

		#for key in self.sensors:
			#print(self.sensors[key])

	def run(self):
		"""
		Thread run function
		
		Args:
			None

		Returns:
			Nothing
		"""

		while (self.should_run == True):
			self.read_sensors()
			time.sleep(2)

class FRUReader:
	"""
	Main class for reading FRU sensor values from EPICS
	"""
	# raw = True

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
		if _crate.host == None:
			_crate.host = os.environ(MTCA_HOST)
			_crate.user = os.environ(MTCA_USER)
			_crate.password = os.environ(MTCA_PASSWORD)

		# Get the information about the sensor
		fn, fru_id, sensor_name = args.split(None, 2)
		self.fru_id = fru_id
		self.sensor_name = sensor_name
		self.fru = get_fru(fru_id)
	
		self.fru.read_sensors()

		self.process = getattr(self, fn)
		self.allowScan = self.fru.scan_list.add

		try:
			rec.UDF = 0
			rec.EGU = self.fru.sensors[self.sensor_name].egu
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

	def update(self, rec, report):
		"""
		Call this function to update the sensor values

		Args:
			rec: database record 
			report: ?

		Returns: 
			Nothing
		"""
		self.read_sensors()

	
