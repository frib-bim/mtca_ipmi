#!/usr/bin/env python3

# File: fan_set_alarms.py
# Date: 2017-12-12
# Author: Wayne Lewis
# 
# Description:
# Set alarms for cooling unit fans. This script will query the MCH to
# get the fan sensor IDs, then use the IDs to set the thresholds.

import argparse
import subprocess

fan_ids = []

def main():
    # Get the arguments
    parser = argparse.ArgumentParser(description = 'Set power module alarms')
    parser.add_argument('--mch',required=True, help='MCH host name or IP address')

    args = parser.parse_args()

    # Build the command to read the sensors
    command = []
    command.append("ipmiutil")
    command.append("sensor")
    command.append("-N")
    command.append(args.mch)

    result = subprocess.check_output(command, universal_newlines=False)

    # Get the list of fan sensor IDs
    for line in result.splitlines():
        line = line.decode('utf8')
        if "Fan" in line:
            fan_ids.append((line.split("snum")[1]).split()[0])

    # Remove duplicate fan IDs. For some reason, the above command repeats each sensor twice.
    unique_fan_ids = list(set(fan_ids))

    # Set the alarm thresholds
    for fan_id in unique_fan_ids:
        command.append("-n")
        command.append(fan_id)
        command.append("-u")
        # Alarm thresholds are lnc:lcr:lnr:unc:ucr:unr
        command.append("1000:500:250:3500:4000:4500")
        result = subprocess.check_output(command, universal_newlines=False)
        print ("Setting thresholds for fan ID {}".format(fan_id))
        del command[-4:]

if __name__ == '__main__':
    main()
