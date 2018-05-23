#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "BDS_MTCA19:MCH_N0019:")
epicsEnvSet("MCH_HOST", "bds-mtca19-mch-n0019")
epicsEnvSet("CRATE_ID", "BDS MTCA 19")
epicsEnvSet("RACK_ID", "BDS-001.05")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

