#!/bin/bash

echo "UDFBackup - $1" | logger -t ARM
/bin/su -l -c "echo /usr/bin/python3 /opt/udfbackup/main.py -d $1 | at now" -s /bin/bash arm
