# Common startup script for MTCA crate monitoring IOC
# This script should be called from each individual IOC startup
# using
# < st_mtca_common.cmd
# after setting the environment variables.

cd $(TOP)

## Register all support components
dbLoadDatabase "dbd/mtcaSensors.dbd"
mtcaSensors_registerRecordDeviceDriver pdbbase

## Load record instances
# Set CU1, CU2 environment variables to override default cooling unit names.
# Set PM environment variables to override default power module name.
dbLoadRecords("db/mtca_crate.db","P=$(CRATE),MCH_HOST=$(MCH_HOST),CRATE_ID=$(CRATE_ID),RACK_ID=$(RACK_ID),CU1=$(CU1=CU01:),CU2=$(CU2=CU02:)")
dbLoadRecords("db/amc_cards.db","P=$(CRATE),PM=$(PM=PM02:)")
dbLoadRecords("db/cooling_unit.template","P=$(CRATE),S=$(CU1=CU01:),UNIT=1")
dbLoadRecords("db/cooling_unit.template","P=$(CRATE),S=$(CU2=CU02:),UNIT=2")
dbLoadRecords("db/power_modules.db","P=$(CRATE)")
dbLoadRecords("db/mch.db","P=$(CRATE),PM=$(PM=PM02:)")

< $(TOP)/iocBoot/archiver_tags.cmd

iocInit()

cd $(TOP)

# This IOC can take >20 s to exit. Please be patient.
