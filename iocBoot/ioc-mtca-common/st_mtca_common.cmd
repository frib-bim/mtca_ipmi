# Common startup script for MTCA crate monitoring IOC
# This script should be called from each individual IOC startup
# using
# < st_mtca_common.cmd
# after setting the environment variables.

epicsEnvSet("AS_PATH", "$(TOP)/as/$(IOC)")

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
dbLoadRecords("db/save_restoreStatus.db","P=$(CRATE)")

# Autosave setup
save_restoreSet_Debug(0)
save_restoreSet_IncompleteSetsOk(1)
save_restoreSet_DatedBackupFiles(1)
save_restoreSet_status_prefix("$(CRATE)")

set_savefile_path("$(AS_PATH)","/sav")

set_pass0_restoreFile("info_settings.sav")
set_pass1_restoreFile("info_settings.sav")

iocInit()
iocLogInit()
caPutLogInit("${EPICS_PUT_LOG_INET}:${EPICS_PUT_LOG_PORT}", 1)

cd $(AS_PATH)/req
makeAutosaveFiles()
create_monitor_set("info_settings.req", 15)

cd $(TOP)

# This IOC can take >20 s to exit. Please be patient.
