#!../../bin/linux-x86_64/mtcaSensors

## You may have to change mtcaSensors to something else
## everywhere it appears in this file

< envPaths

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/mtcaSensors.dbd"
mtcaSensors_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadRecords("db/mtca_crate.db","P=MTCA:TEST1:")
dbLoadRecords("db/schroff_utca_cu.db","P=MTCA:TEST1:30_97:,FRU_ID=30.97")

cd "${TOP}/iocBoot/${IOC}"
iocInit

