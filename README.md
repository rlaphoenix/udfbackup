# UDFBackup
Automatic and Headless UDF Disc Backup Utility, supporting CD's, DVD's, HD-DVD's and Blu-Ray's.  
Simply insert a disc in 1 or more drive's and it will automatically backup then eject all discs.

## Features
- Automated; Detect's disc insertion via udev rules.
- Headless; No UI, No user interaction, just automated.
- Parallel; Can be used with multiple disc's and multiple drive's.

## Installation
*only linux is supported, udev is not available on windows*

First, you need to set up your `/etc/fstab` configuration to set where your drives mount to.  
The mount folder has to be specific. For example `/dev/sr0` would need to be mounted to `/mnt/dev/sr0`.  
Perhaps a reader can figure out a way to obtain the mount location via pythonudf or such so this isn't necessary?

Example fstab entries:

```
# <file system> <dir>         <type>  <options>              <dump>  <pass>
/dev/sr0        /mnt/dev/sr0  auto    user,noauto,exec,utf8  0       0
/dev/sr1        /mnt/dev/sr1  auto    user,noauto,exec,utf8  0       0
/dev/sr2        /mnt/dev/sr2  auto    user,noauto,exec,utf8  0       0
```

Now do the following:
```
git clone https://github.com/imPRAGMA/udfbackup
cd udfbackup
sudo mkdir -p /opt/udfbackup
sudo mv data/* /opt/udfbackup/
sudo ln -s /opt/udfbackup/51-automedia.rules /lib/udev/rules.d/
cd ../ && rm -r udfbackup
```

Now, you need to edit `/opt/udfbackup/main.py` and set the `OUTPUT` directory to wherever you wish (your user needs permissions there).  
Finally, reboot your PC and the entire system will be configured and good to go! :O

## Uninstallation
```
sudo rm -r /opt/udfbackup
reboot
```
That all, you can remove the fstab entries if you wish but it won't interfere with anything.

## [License](LICENSE)