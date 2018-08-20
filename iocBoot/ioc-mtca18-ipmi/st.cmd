#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "BDS_MTCA18:MCH_N0018:")
epicsEnvSet("MCH_HOST", "bds-mtca18-mch-n0018")
epicsEnvSet("CRATE_ID", "BDS MTCA 18")
epicsEnvSet("RACK_ID", "BDS-001.04")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

