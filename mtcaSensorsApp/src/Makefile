TOP=../..

include $(TOP)/configure/CONFIG
include $(PYDEVSUP)/configure/CONFIG_PY
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = mtcaSensors
# mtcaSensors.dbd will be created and installed
DBD += mtcaSensors.dbd

# mtcaSensors.dbd will be made up from these files:
mtcaSensors_DBD += base.dbd
mtcaSensors_DBD += pyDevSup.dbd

# Add all the support libraries needed by this IOC
mtcaSensors_LIBS += pyDevSup$(PY_LD_VER)

# mtcaSensors_registerRecordDeviceDriver.cpp derives from mtcaSensors.dbd
mtcaSensors_SRCS += mtcaSensors_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
mtcaSensors_SRCS_DEFAULT += mtcaSensorsMain.cpp
mtcaSensors_SRCS_vxWorks += -nil-

#PY += FRU.py
PY += MTCACrate.py

# Finally link to the EPICS Base libraries
mtcaSensors_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(DIAGSTD)/configure/fribdiagstdMakefile
include $(TOP)/configure/RULES
include $(PYDEVSUP)/configure/RULES_PY
#----------------------------------------
#  ADD RULES AFTER THIS LINE

