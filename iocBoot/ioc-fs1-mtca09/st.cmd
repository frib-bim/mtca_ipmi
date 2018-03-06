#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "FS1_MTCA09:MCH_N0009:")
epicsEnvSet("MCH_HOST", "fs1-mtca09-mch-n0009")
epicsEnvSet("CRATE_ID", "FS1 MTCA 09")
epicsEnvSet("RACK_ID", "FS1-003.02")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

