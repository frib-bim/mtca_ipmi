#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS3_MTCA16:MCH_N0016:")
epicsEnvSet("MCH_HOST", "ls3-mtca16-mch-n0016")
epicsEnvSet("CRATE_ID", "LS3 MTCA 16")
epicsEnvSet("RACK_ID", "LS3-011.08")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

