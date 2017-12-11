#!/usr/bin/env python3

# File: power_module_set_alarms.py
# Date: 2017-12-04
# Author: Wayne Lewis
# 
# Description:
# Set alarms for current readings in MTCA crate power module

import argparse
import subprocess
import time 

thresholds = ["lnc", "unr", "ucr", "unc"]

def main():
    # Get the arguments
    parser = argparse.ArgumentParser(description = 'Set power module alarms')
    parser.add_argument('--mch',required=True, help='MCH host name or IP address')
    parser.add_argument('--lnc',default=0.0001,required=False, help='Channel lower non-critical thresold')
    parser.add_argument('--unc',default=3.9,required=False, help='Channel upper non-critical thresold')
    parser.add_argument('--ucr',default=4.0,required=False, help='Channel upper critical thresold')
    parser.add_argument('--unr',default=4.1,required=False, help='Channel upper non-recoverable thresold')
    parser.add_argument('--lnc_sum',default=1.0,required=False, help='Sum lower non-critical thresold')
    parser.add_argument('--unc_sum',default=15.0,required=False, help='Sum upper non-critical thresold')
    parser.add_argument('--ucr_sum',default=16.0,required=False, help='Sum upper critical thresold')
    parser.add_argument('--unr_sum',default=18.0,required=False, help='Sum upper non-recoverable thresold')

    args = parser.parse_args()

    command = []
    command.append("ipmitool")
    command.append("-H")
    command.append(args.mch)
    command.append("-A")
    command.append("None")
    command.append("sensor")
    command.append("thresh")

    # Set the channel alarm thresholds
    for ch in range(1,17):
        command.append("Ch{:02d} Current".format(ch))
        # Appears to require two calls to get alarms to stick
        for call in range(0,2):
            for threshold in thresholds:
                command.append(threshold)
                command.append("{}".format(getattr(args,threshold)))
                subprocess.call(command)

                # Delete the old threshold name and value
                del command[-2:]
        
        # Delete the old sensor name
        del command[-1:]

    # Set the total current thresholds
    command.append("Current(Sum)")
    for call in range(0,2):
        for threshold in thresholds:
            command.append(threshold)
            command.append("{}".format(getattr(args,threshold+"_sum")))
            subprocess.call(command)

            # Delete the old threshold name and value
            del command[-2:]

if __name__ == '__main__':
    main()
