#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "MTCAMCH03:")
epicsEnvSet("MCH_HOST", "mtcamch03")

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/mtcaSensors.dbd"
mtcaSensors_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadRecords("db/mtca_crate.db","P=$(CRATE),MCH_HOST=$(MCH_HOST)")
dbLoadRecords("db/amc_cards.db","P=$(CRATE)")


cd "${TOP}/iocBoot/${IOC}"
iocInit

