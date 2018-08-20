#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS2_MTCA12:MCH_N0012:")
epicsEnvSet("MCH_HOST", "ls2-mtca12-mch-n0012")
epicsEnvSet("CRATE_ID", "LS2 MTCA 12")
epicsEnvSet("RACK_ID", "LS2-017.08")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

