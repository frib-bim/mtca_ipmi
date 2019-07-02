#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS3_MTCA17:MCH_N0017:")
epicsEnvSet("MCH_HOST", "ls3-mtca17-mch-n0017")
epicsEnvSet("CRATE_ID", "LS3 MTCA 17")
epicsEnvSet("RACK_ID", "LS3_R1624:CAB_N2101")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

