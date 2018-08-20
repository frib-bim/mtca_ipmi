#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "FS1_MTCA10:MCH_N0010:")
epicsEnvSet("MCH_HOST", "fs1-mtca10-mch-n0010")
epicsEnvSet("CRATE_ID", "FS1 MTCA 10")
epicsEnvSet("RACK_ID", "FS1-005.06")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

