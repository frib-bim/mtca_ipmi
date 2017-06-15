#!/usr/bin/env python
# File: FRU.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get sensor information for FRU
# FRU = Field Replaceable Unit
#

#from devsup.db import IOScanListBlock
#from devsup.util import StoppableThread
import threading
import time
from subprocess import check_output

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

		#self.scan_list = IOScanListBlock()
		
		super(FRUScanner, self).__init__()
		
		# Initialize list of FRUs
		self.sensors = {}

		self.should_run = True

	def populate_sensors(self):
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

		for key in self.sensors:
			print(self.sensors[key])

	def run(self):
		"""
		Thread run function
		
		Args:
			None

		Returns:
			Nothing
		"""

		while (self.should_run == True):
			self.populate_sensors()
			time.sleep(2)

def main():
	fru_fgpdb = get_fru("193.102")
	fru_fgpdb.host = "mtcamch04"
	fru_fgpdb.user = "root"
	fru_fgpdb.password = "ctsFree4All"
	fru_fgpdb.should_run = True
	fru_fgpdb.start()
	
	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		print "exiting"
		fru_fgpdb.should_run = False
		fru_fgpdb.join()
		print "exited thread"

if __name__ == "__main__":
	main()

