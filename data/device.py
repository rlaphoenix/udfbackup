# Standard Library
import os
import time
import logging
import subprocess
import shlex
import fcntl
import traceback
import shutil
from enum import Enum
# PyPI packages
import pyudev
# Custom scripts
import utils

#############################################################
# Exit Codes:                                               #
# 1 : Unable to open device to check status                 #
# 2 : Device not ready (device status)                      #
# 3 : Device not ready (ID_CDROM_MEDIA_STATE)               #
# 4 : Disc could not be identified                          #
# 5 : Disc Type not yet implemented                         #
# 6 : Child-process returned non-zero exit code             #
# 7 : Child-process returned exception                      #
# 8 : Exception occured when dealing with a child-process   #
#############################################################

class Device(object):

    class DeviceStatus(Enum):
        CDS_NO_INFO = 0
        CDS_NO_DISC = 1
        CDS_TRAY_OPEN = 2
        CDS_DRIVE_NOT_READY = 3
        CDS_DISC_OK = 4
    
    class DiscType(Enum):
        UNKNOWN = 0
        DATA = 1
        CD = 2
        DVD = 3
        BD = 4

    def __init__(self, device, base_dir):
        self.device = device
        self.base_dir = os.path.expanduser(base_dir)
        self.out_dir = None
        self.status = self.get_status()
        self.mountpoint = f"/mnt{device}"
        self.disctype = self.DiscType.UNKNOWN
        self.label = None
        # Create a Logger
        logging.basicConfig(
            #filename=os.path.join(directory, "info.log"),
            format=f"[{os.getpid()}] [%(asctime)s] %(levelname)s UDFBackup: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level="INFO",
            handlers=[
                logging.FileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)), "info.log")),
                logging.StreamHandler()
            ]
        )
        # Start loading the device metadata
        self.load()
        # Start backing up
        self.backup()

    def load(self):
        # Make sure it's loaded and ready to go
        if self.status != self.DeviceStatus.CDS_DISC_OK:
            self.exit(f"Device is not ready for backup, aborting. ({self.status.name})", 2)
        # Get Disc Type
        context = pyudev.Context()
        device = pyudev.Devices.from_device_file(context, self.device)
        if "ID_CDROM_MEDIA_STATE" not in device or device["ID_CDROM_MEDIA_STATE"] != "complete":
            self.exit(f"Device is not ready for backup, aborting. (ID_CDROM_MEDIA_STATE={device['ID_CDROM_MEDIA_STATE']})", 3)
        if "ID_FS_LABEL" in device:
            self.label = device["ID_FS_LABEL"]
        if "ID_CDROM_MEDIA_TRACK_COUNT_AUDIO" in device:
            self.disctype = self.DiscType.CD
        if "ID_CDROM_MEDIA_DVD" in device:
            self.disctype = self.DiscType.DVD
        if "ID_CDROM_MEDIA_BD" in device:
            self.disctype = self.DiscType.BD
        if self.disctype == self.DiscType.UNKNOWN:
            self.exit(f"Could not identify disc in {self.device}, aborting.", 4)
        logging.info(f"{self.disctype.name} inserted into {self.device} called {self.label}, backing it up!")
        # Create a base hidden directory to indicate that it is not yet finished
        self.out_dir = os.path.join(self.base_dir, f".{self.label}_{round(time.time() * 100)}")
        utils.makedirs(self.out_dir)
        # Make a log of the current device object as it's fully prepped
        for l in str(self).splitlines()[1:]:
            logging.info(l)
    
    def backup(self):
        logging.info(f"Starting {self.disctype.name} Backup")
        if self.disctype == self.DiscType.BD:
            # Get MakeMKV disc number
            mdisc = subprocess.check_output(
                args=f"makemkvcon -r info disc:9999 | grep {self.device} | grep -oP '(?<=:).*?(?=,)'",
                shell=True
            ).decode("utf-8").strip()
            # Use the Disc Number and MakeMKV's backup and decrypt feature for the disc
            subprocess.run(
                f"makemkvcon backup --decrypt -r disc:{mdisc} {shlex.quote(self.out_dir)}",
                shell=True
            )
        elif self.disctype == self.DiscType.DVD:
            # Use dvdbackup's mirror backup feature
            self.run([
                "dvdbackup",
                "--input", self.device,                 # choose device to dump from
                "--progress", "--verbose", "--mirror",  # show progress, be verbose, backup full disc
                "--error", "a",                         # if a read error occurs, abort
                "--output", self.base_dir,
                "--name", os.path.basename(self.out_dir)
            ])
        else:
            # todo ; to be implemented
            self.exit("This Disc type is not yet implemented. Sorry.", 5)
        # Finished, let's move the directory so that it isn't in a hidden folder
        os.rename(self.out_dir, os.path.join(self.base_dir, os.path.basename(self.out_dir)[1:]))
        # Eject the finished disc
        self.eject()
        # Log the completion
        logging.info(f"Completed backup for {self.device} ({self.label})")

    def get_status(self):
        """Get the status code of the cdrom device"""
        try:
            fd = os.open(self.device, os.O_RDONLY | os.O_NONBLOCK)
        except Exception:
            self.exit(f"Failed to open device {self.device} to check it's status.", 1)
        return self.DeviceStatus(fcntl.ioctl(fd, 0x5326, 0))

    def eject(self):
        """Eject disc"""
        os.system(f"eject {self.device}")
    
    def run(self, args, get_text=False):
        logging.info(f"Calling {args}")
        try:
            p = subprocess.run(args, check=False, capture_output=True)
            if p.stdout:
                logging.debug(" ".join(args))
                logging.debug(p.stdout.decode().strip())
            if p.stderr:
                logging.error(p.stderr.decode().strip())
            if p.returncode != 0:
                self.exit(f"Child-process {args[0]} returned a non-zero exit code!", 6)
            if p.stderr:
                self.exit(f"Child-process {args[0]} returned an exception!", 7)
            if get_text and p.stdout:
                return p.stdout.decode().strip()
        except:
            self.exit(f"An exception occured when dealing with a child-process!\nArguments: {args}\n{traceback.format_exc()}", 8)
    
    def exit(self, exitmsg, exitcode=0):
        """
        Exit handler specifically crafted to clean up any made files on errors
        """
        if exitmsg:
            logging.error(exitmsg)
        # If the name exist's then we probably started dumping, let's make sure to delete the error'd backup
        if self.out_dir and os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)
        exit(exitcode)

    def __str__(self):
        """Returns a string of the object"""
        s = self.__class__.__name__ + ":"
        for attr, value in self.__dict__.items():
            s += f"\n{attr}: {value}"
        return s
