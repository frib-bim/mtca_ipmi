#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA03:MCH_N0003:")
epicsEnvSet("MCH_HOST", "ls1-mtca03-mch-n0003")
epicsEnvSet("CRATE_ID", "LS1 MTCA 03")
epicsEnvSet("RACK_ID", "LS1-003.06")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

