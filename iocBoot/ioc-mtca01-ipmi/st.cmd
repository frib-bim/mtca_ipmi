#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "FE_MTCA01:MCH_N0001:")
epicsEnvSet("MCH_HOST", "fe-mtca01-mch-n0102")
epicsEnvSet("CRATE_ID", "FE MTCA 01")
epicsEnvSet("RACK_ID", "FE-001.06")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

