#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA07:MCH_N0007:")
epicsEnvSet("MCH_HOST", "ls1-mtca07-mch-n0007")
epicsEnvSet("CRATE_ID", "LS1 MTCA 07")
epicsEnvSet("RACK_ID", "LS1-019.02")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

