#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA06:MCH_N0006:")
epicsEnvSet("MCH_HOST", "ls1-mtca06-mch-n0006")
epicsEnvSet("CRATE_ID", "LS1 MTCA 06")
epicsEnvSet("RACK_ID", "FE-004.04")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

