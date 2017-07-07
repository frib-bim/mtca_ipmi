#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "MTCAMCH04:")
epicsEnvSet("MCH_HOST", "mtcamch04")
epicsEnvSet("CRATE_ID", "MTCA 03")
epicsEnvSet("RACK_ID", "Office")

< envPaths

< $(TOP)/iocBoot/ioc-mtca-common/st_mtca_common.cmd

