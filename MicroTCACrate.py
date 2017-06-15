#!/usr/bin/env python
# File: FRU.py
# Date: 2017-06-15
# Author: Wayne Lewis
#
# Description: Get FRU information for microTCA crate.
# FRU = Field Replaceable Unit
#
# Macros:
# P: Device prefix

#from devsup.db import IOScanListBlock
#from devsup.util import StoppableThread
import threading
from subprocess import check_output

_crates = {}

def get_crate(host):
	"""
	Find existing crate object, or create new one.

	Args:
		host: host name of crate MCH

	Returns: 
		MicroTCACrateScanner object
	"""
	try:
		return _crates[host]
	except KeyError:
		crate = MicroTCACrateScanner(host)
		_crates[host] = crate
		return crate

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

#class MicroTCACrateScanner(StoppableThread)
# TODO: work out if this should be a thread or just processed from EPICS

class MicroTCACrateScanner(threading.Thread):
	"""
	Class for identifying FRUs in microTCA crate.
	"""
	
	def __init__(self, host):
		"""
		Initializer for MicroTCACrateScanner object.

		Args:
			host: host name of MCH in crate

		Returns:
			Nothing
		"""

		self.host = host
		self.user = None
		self.password = None

		#self.scan_list = IOScanListBlock()
		
		super(MicroTCACrateScanner, self).__init__()
		
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
		
		print result

		for line in result.splitlines():
			try:
				print line
				name, ref, status, id, desc = line.split('|')
				self.frus.append(FRU(name=name.strip(), id=id.strip()))
			except ValueError:
				print "Couldn't parse {}".format(line)

		for fru in self.frus:
			print(fru)


def main():
	crate1 = get_crate("mtcamch04")
	crate1.user = "root"
	crate1.password = "ctsFree4All"
	crate1.populate_fru_list()

if __name__ == "__main__":
	main()

