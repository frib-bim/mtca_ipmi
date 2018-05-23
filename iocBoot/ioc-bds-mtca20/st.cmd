#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "BDS_MTCA20:MCH_N0020:")
epicsEnvSet("MCH_HOST", "bds-mtca20-mch-n0020")
epicsEnvSet("CRATE_ID", "BDS MTCA 20")
epicsEnvSet("RACK_ID", "BDS-004.03")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

