#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA05:MCH_N0005:")
epicsEnvSet("MCH_HOST", "ls1-mtca05-mch-n0005")
epicsEnvSet("CRATE_ID", "LS1 MTCA 05")
epicsEnvSet("RACK_ID", "LS1-011.02")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

