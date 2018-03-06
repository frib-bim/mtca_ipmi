#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS1_MTCA08:MCH_N0008:")
epicsEnvSet("MCH_HOST", "ls1-mtca08-mch-n0008")
epicsEnvSet("CRATE_ID", "LS1 MTCA 08")
epicsEnvSet("RACK_ID", "LS1-023.02")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

