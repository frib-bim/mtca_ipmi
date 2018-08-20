#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS2_MTCA11:MCH_N0011:")
epicsEnvSet("MCH_HOST", "ls2-mtca11-mch-n0011")
epicsEnvSet("CRATE_ID", "LS2 MTCA 11")
epicsEnvSet("RACK_ID", "LS2-008.08")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

