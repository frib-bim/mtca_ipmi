# MTCA sensor IOC

## Summary 

This IOC monitors the sensors in an MTCA crate.

## Prerequisites

### Command line tools
- ``ipmitool`` 
This has been tested against ipmitool version 1.8.11

### EPICS modules

- ``pyDevSup`` 
- ``autosave``

# Python packages
- ``numpy``
- ``re``
- ``math``
- ``time``
- ``os``

## Usage

For each new chassis, create a new directory under iocBoot. Copy one of the
existing crate directories (e.g., ioc-mtca01). Modify the environment variables
for the new crate. 

Most of the IOC commands are in the common startup script located in
$(TOP)/iocBoot/ioc-mtca-common/st-mtca-common.cmd




