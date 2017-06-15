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
		return _frus[host]
	except KeyError:
		fru = FRUScanner(id)
		_frus[host] = fru
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
		return "Name: {}".format(self.name)

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

		#self.scan_list = IOScanListBlock()
		
		super(FRUScanner, self).__init__()
		
		# Initialize list of FRUs
		self.sensors = {}

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
		
		print result

		for line in result.splitlines():
			try:
				print line
				name, sensor_id, status, fru_id, val = line.split('|')
				value, egu = val.split(' ', 1)
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
				print "Couldn't parse {}".format(line)

		for sensor in self.sensors:
			print(sensor)


def main():
	fru_fgpdb = get_fru("193.102")
	crate1.user = "root"
	crate1.password = "ctsFree4All"
	crate1.populate_sensors()

if __name__ == "__main__":
	main()

