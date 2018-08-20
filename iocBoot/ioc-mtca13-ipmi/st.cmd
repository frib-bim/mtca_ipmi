#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "LS2_MTCA13:MCH_N0013:")
epicsEnvSet("MCH_HOST", "ls2-mtca13-mch-n0013")
epicsEnvSet("CRATE_ID", "LS2 MTCA 13")
epicsEnvSet("RACK_ID", "LS2-023.08")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

