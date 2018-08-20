#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "FS2_MTCA15:MCH_N0015:")
epicsEnvSet("MCH_HOST", "fs2-mtca15-mch-n0015")
epicsEnvSet("CRATE_ID", "FS2 MTCA 15")
epicsEnvSet("RACK_ID", "FS2-001.08")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

