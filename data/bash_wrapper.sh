#!/usr/bin/env bash

export XAUTHORITY=/home/owner/.Xauthority
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus"

/usr/bin/python3 /opt/udfbackup/__init__.py -d $1