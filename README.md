# UDFBackup
Automatic and Headless UDF Disc Backup Utility.  
Simply insert a disc in 1 or more drive's and it will automatically backup then eject all discs.

## Features
- Automated; Detect's disc insertion via udev rules.
- Headless; No UI, No user interaction, just automated.
- Parallel; Can be used with multiple disc's and multiple drive's.
- DVD and Blu-Ray supported; with more to come.

## Requirements
- Linux machine
- Python 3 (and python-pip)
- dvdbackup
- makemkv (and makemkvcon)
- git
- at (http://software.calhariz.com/at)

All of these requirement's can be gotten from your Linux Distro's Repo.

## Installation
```
git clone https://github.com/imPRAGMA/udfbackup
cd udfbackup
sudo pip3 install -r requirements.txt
sudo mkdir -p /opt/udfbackup
sudo mv data/* /opt/udfbackup/
sudo ln -s /opt/udfbackup/51-automedia.rules /lib/udev/rules.d/
cd ../ && rm -r udfbackup
```
In `/opt/udfbackup/bash_wrapper.sh` change the `USERNAME` and `OUTPUT_D` variables to your needs. The `USERNAME` need's permission to read, write and rename file's in the specified `OUTPUT_D` directory.
Finally, reboot your PC and the entire system will be configured and good to go! :O

Go insert a disc after rebooting and it will spin up!  
Backups are created in a hidden directory in the specified `OUTPUT_D` (`.` at start of the directory name).  
Once the Backup has finished, it will unhide the directory to indicate that you can mess with it however you like now.

## Uninstallation
```
sudo rm -r /opt/udfbackup
```
That all, but I recommend rebooting just in case there's any old settings or stuff at play.

## [License](LICENSE)