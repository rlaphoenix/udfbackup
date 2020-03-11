# UDFBackup

Automatic and Headless UDF Disc Backup Utility.  
Simply insert a disc in 1 or more drive's and it will automatically backup then eject all discs.

<p align="center">
<a href="https://python.org"><img src="https://img.shields.io/badge/python-3.7%2B-informational?style=flat-square" /></a>
<a href="https://github.com/rlaPHOENiX/udfbackup/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/rlaPHOENiX/udfbackup?style=flat-square"></a>
<a href="https://github.com/rlaPHOENiX/udfbackup/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/rlaPHOENiX/udfbackup?style=flat-square"></a>
<a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square"></a>
</p>

## Features

- Automated; Detect's disc insertion via udev rules.
- Headless; No UI, No user interaction, just automated.
- Parallel; Can be used with multiple disc's and multiple drive's.
- DVD and Blu-Ray supported; with more to come.

## To-do list

- [ ] Generic Data Disc Support
- [ ] CD Support
- [x] DVD Support
- [x] Blu-Ray Support
- [x] UHD Blu-Ray Support
- [ ] Region Lock Removal
- [ ] ISO Support with accurate 1:1 metadata

## Requirements

- [Linux](https://wikipedia.org/wiki/Linux)
- [Python 3 and pip](https://python.org)
- [dvdbackup](http://dvdbackup.sourceforge.net)
- [makemkv and makemkvcon](https://makemkv.com)
- [git](https://git-scm.com)
- [at](http://software.calhariz.com/at)

All of these requirement's can be gotten from your Linux Distribution's Package Repository.

## Installation

```
git clone https://github.com/imPRAGMA/udfbackup
cd udfbackup
sudo pip3 install -r requirements.txt
sudo mkdir -p /opt/udfbackup
sudo mv data/* /opt/udfbackup/
sudo ln -s /opt/udfbackup/51-automedia.rules /lib/udev/rules.d/
cd ../ && rm -r udfbackup
sudo udevadm control --reload
```

Open `/opt/udfbackup/bash_wrapper.sh`, change the `USERNAME` and `OUTPUT_D` variables to your needs, making sure read/write/rename/delete permissions are available for the username and output directory combination.

:tada:

Insert disc's and let it spin up! Backups are created in hidden folders in the specified `OUTPUT_D` (`.` at start of the directory name).  
Once the Backup has finished, it will unhide the directory to indicate that you can mess with it however you like now.
If the hidden folder get's deleted, then something failed, check the `info.log` file which will be next to the `device.py` file. If you followed the instructions exactly, then it's location is `/opt/udfbackup/info.log`.

## Uninstallation

```
sudo rm -r /opt/udfbackup
sudo udevadm control --reload
```

Yep, that's all that need's to be done.

## [License](LICENSE)
