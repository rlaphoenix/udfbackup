#!/usr/bin/python3

import argparse
from device import Device

# Parse Arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--device", help="Device Path from UDEV", required=True)
ap.add_argument("-f", "--folder", help="Folder Path to output the backups", required=True)
args = ap.parse_args()

# Start! :D
Device(
    device=f"/dev/{args.device[:3]}",
    base_dir=args.folder
)
