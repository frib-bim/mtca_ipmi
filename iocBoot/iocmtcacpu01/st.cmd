#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

epicsEnvSet("CRATE", "MTCAMCH04:")

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/mtcaSensors.dbd"
mtcaSensors_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadRecords("db/mtca_crate.db","P=$(CRATE)")
#dbLoadRecords("db/schroff_utca_cu.db","P=$(CRATE)30_97:,FRU_ID=30.97")
#dbLoadRecords("db/fgpdb.db","P=$(CRATE)193_102:,FRU_ID=193.102")
#dbLoadRecords("db/sis8300.db","P=$(CRATE)193_101:,FRU_ID=193.101")
dbLoadRecords("db/amc_cards.db","P=$(CRATE)")


cd "${TOP}/iocBoot/${IOC}"
iocInit

