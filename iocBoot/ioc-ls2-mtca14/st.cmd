#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS2_MTCA14:MCH_N0014:")
epicsEnvSet("MCH_HOST", "ls2-mtca14-mch-n0014")
epicsEnvSet("CRATE_ID", "LS2 MTCA 14")
epicsEnvSet("RACK_ID", "LS2-042.02")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

