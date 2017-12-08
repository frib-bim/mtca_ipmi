#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA04:MCH_N0002:")
epicsEnvSet("MCH_HOST", "ls1-mtca04-mch-n0002")
epicsEnvSet("CRATE_ID", "LS1 MTCA 04")
epicsEnvSet("RACK_ID", "LS1-002.06")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

