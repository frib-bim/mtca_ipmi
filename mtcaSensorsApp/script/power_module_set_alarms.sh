#!/bin/bash

# File: power_module_set_alarms.sh
# Date: 2017-06-26
# Author: Wayne Lewis
# 
# Description:
# Set alarms for current readings in MTCA crate power module

# Adjust these variables as required
mtcamch="mtcamch03"
i_lnc=0.1
i_unc=1.9
i_ucr=2.0
i_unr=2.1
i_total_lnc=1.0
i_total_unc=15
i_total_ucr=16
i_total_unr=18

# Set the channel alarm thresholds
for ch in {01..16}
	do echo 'Ch'"$ch"' Current'
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Ch'"$ch"' Current' lnc "$i_lnc"
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Ch'"$ch"' Current' unc "$i_unc"
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Ch'"$ch"' Current' ucr "$i_ucr"
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Ch'"$ch"' Current' unr "$i_unr"
done

# Set the total alarm thresholds
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Current(Sum)' lnc "$i_total_lnc"
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Current(Sum)' unc "$i_total_unc"
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Current(Sum)' ucr "$i_total_ucr"
    ipmitool -H "$mtcamch" -U root -P ctsFree4All sensor thresh 'Current(Sum)' unr "$i_total_unr"


