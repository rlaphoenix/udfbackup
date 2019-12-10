#!/usr/bin/python3

import argparse
from device import Device

# Parse Arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--device", help="Device Path from UDEV", required=True)
args = ap.parse_args()

# Get Arguments
DEVICE = f"/dev/{args.device[:3]}"
OUTPUT = "/home/owner/Videos"  # Change this! Don't use ~ as that will link to `root` user's home directory, not yours

# Start! :D
Device(DEVICE, OUTPUT)
