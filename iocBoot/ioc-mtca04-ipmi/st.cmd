#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA04:MCH_N0004:")
epicsEnvSet("MCH_HOST", "ls1-mtca04-mch-n0004")
epicsEnvSet("CRATE_ID", "LS1 MTCA 04")
epicsEnvSet("RACK_ID", "LS1-006.04")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

