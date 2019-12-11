#!/usr/bin/env bash

export XAUTHORITY=/home/owner/.Xauthority
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1000/bus"

USERNAME=pragma
OUTPUT_D=~/Videos  # Change this! Just remember ~ will point to the home directory of the USERNAME you set.

/bin/su -l -c "echo /usr/bin/python3 /opt/udfbackup/__init__.py -d $1 | at now" -s /bin/bash $USERNAME
