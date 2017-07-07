# MTCA sensor IOC

## Summary 

This IOC monitors the sensors in an MTCA crate.

## Prerequisites

### Command line tools
- ``ipmitool`` 

This has been tested against ipmitool version 1.8.11 Recommended version is
1.8.11. This can be built from source at:

https://sourceforge.net/projects/ipmitool/files/ipmitool/1.8.17/ipmitool-1.8.11.tar.bz2

1.8.14 breaks the alarm settings part. 1.8.14 is installed by apt-get on
jessie.

1.8.17 works again, except for the firmware. Source:

https://sourceforge.net/projects/ipmitool/files/ipmitool/1.8.17/ipmitool-1.8.17.tar.bz2

- ``ipmiutil``

Tested with 3.05.

Built from source at:

http://sourceforge.net/projects/ipmiutil/files/ipmiutil-3.0.5.tar.gz

### EPICS modules

- ``pyDevSup`` 
- ``autosave``

# Python packages
- ``numpy``
- ``re``
- ``math``
- ``time``
- ``os``
- ``subprocess`` or ``subprocess32``

For Python2.7 systems, the ``subprocess32`` module needs to be installed:

``sudo pip install subprocess32``

## Usage

For each new chassis, create a new directory under iocBoot. Copy one of the
existing crate directories (e.g., ioc-mtca01). Modify the environment variables
for the new crate. 

Most of the IOC commands are in the common startup script located in
$(TOP)/iocBoot/ioc-mtca-common/st-mtca-common.cmd




