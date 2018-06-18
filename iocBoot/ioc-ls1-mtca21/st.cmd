#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA21:MCH_N0021:")
epicsEnvSet("MCH_HOST", "ls1-mtca21-mch-n0021")
epicsEnvSet("CRATE_ID", "LS1 MTCA 21")
epicsEnvSet("RACK_ID", "D-STATION")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

