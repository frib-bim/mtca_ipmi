#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "DIAG_MTCA99:MCH_N0099:")
epicsEnvSet("MCH_HOST", "mtca99-mch")
epicsEnvSet("CRATE_ID", "MTCA 99")
epicsEnvSet("RACK_ID", "Dev net")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

