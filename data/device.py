# Standard Library
import os
import time
import logging
import subprocess
import shlex
import fcntl
from enum import Enum
# PyPI packages
import pyudev
# Custom scripts
import utils

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
        self.base_dir = base_dir
        self.out_name = None
        self.status = self.get_status()
        self.mountpoint = f"/mnt{device}"
        self.disctype = self.DiscType.UNKNOWN
        self.label = None
        self.ejected = False
        # Create a Logger
        self.create_logger()
        # Start loading the device metadata
        self.load()
        # Start backing up
        self.backup()

    def __str__(self):
        """Returns a string of the object"""
        s = self.__class__.__name__ + ":"
        for attr, value in self.__dict__.items():
            s += f"\n{attr}: {value}"
        return s

    def load(self):
        # Make sure it's loaded and ready to go
        if self.status != self.DeviceStatus.CDS_DISC_OK:
            logging.error(f"Device is not ready for backup, aborting. ({self.status.name})")
            exit()
        # Get Disc Type
        context = pyudev.Context()
        device = pyudev.Devices.from_device_file(context, self.device)
        if "ID_CDROM_MEDIA_STATE" not in device or device["ID_CDROM_MEDIA_STATE"] != "complete":
            logging.error(f"Device is not ready for backup, aborting. (ID_CDROM_MEDIA_STATE)")
            exit()
        if "ID_FS_LABEL" in device:
            self.label = device["ID_FS_LABEL"]
        if "ID_CDROM_MEDIA_TRACK_COUNT_AUDIO" in device:
            self.disctype = self.DiscType.CD
        if "ID_CDROM_MEDIA_DVD" in device:
            self.disctype = self.DiscType.DVD
        if "ID_CDROM_MEDIA_BD" in device:
            self.disctype = self.DiscType.BD
        # Notify the user the disc state
        if self.disctype == self.DiscType.UNKNOWN:
            logging.error(f"Could not identify disc in {self.device}, aborting.")
            self.notify(f"Could not identify disc in {self.device}, aborting.")
            exit()
        self.notify(f"{self.disctype.name} inserted into {self.device} called {self.label}, backing it up!")
        # Create a base hidden directory to indicate that it is not yet finished
        self.out_name = f".{self.label}_{round(time.time() * 100)}"
        utils.makedirs(os.path.join(self.base_dir, self.out_name))
        # Make a log of the current device object as it's fully prepped
        for l in str(self).splitlines()[1:]:
            logging.info(l)
    
    def backup(self):
        logging.info(f"Backing up {self.disctype.name}")
        if self.disctype == self.DiscType.BD:
            # Get MakeMKV disc number
            mdisc = subprocess.check_output(
                args=f"makemkvcon -r info disc:9999 | grep {self.device} | grep -oP '(?<=:).*?(?=,)'",
                shell=True
            ).decode("utf-8").strip()
            # Use the Disc Number and MakeMKV's backup and decrypt feature for the disc
            subprocess.run(
                f"makemkvcon backup --decrypt -r disc:{mdisc} {shlex.quote(os.path.join(self.base_dir, self.out_name))}",
                shell=True
            )
        elif self.disctype == self.DiscType.DVD:
            logging.info("Running dvdbackup")
            try:
                # Use dvdbackup's mirror backup feature
                p = subprocess.run([
                    "dvdbackup",
                    "--input", self.device,            # choose device to dump from
                    "--progress", "--verbose", "--mirror",  # show progress, be verbose, backup full disc
                    "--error", "a",                         # if a read error occurs, abort
                    "--output", self.base_dir,
                    "--name", self.out_name
                ], check=False, capture_output=False)
                if p.stderr:
                    logging.error(p.stderr.decode().strip())
                    self.notify(f"{self.disctype.name} backup failed! Check log for more information!")
                    exit()
                if p.stdout:
                    logging.info(p.stdout.decode().strip())
            except:
                logging.info("Exception occured! :(")
                import sys
                e = sys.exc_info()[0]
                logging.info(e)
            logging.info("Finished dvdbackup")
        else:
            # to be implemented
            pass
        # Finished, let's move the directory so that it isn't in a hidden folder
        os.rename(os.path.join(self.base_dir, self.out_name), os.path.join(self.base_dir, self.out_name[1:]))
        # Eject the finished disc
        self.eject()
    
    def create_logger(self, directory=os.path.dirname(os.path.realpath(__file__))):
        """
        Setup logging and return the path to the logfile for
        redirection of external calls
        """
        logging.basicConfig(
            #filename=os.path.join(directory, "info.log"),
            format=f"[{os.getpid()}] [%(asctime)s] %(levelname)s UDFBackup: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level="INFO",
            handlers=[
                logging.FileHandler(os.path.join(directory, "info.log")),
                logging.StreamHandler()
            ]
        )

    def get_status(self):
        """
        Get the status code of the cdrom device
        """
        try:
            fd = os.open(self.device, os.O_RDONLY | os.O_NONBLOCK)
        except Exception:
            logging.error(f"Failed to open device {self.device} to check it's status.")
            exit(1)
        return self.DeviceStatus(fcntl.ioctl(fd, 0x5326, 0))

    def eject(self):
        """Eject disc"""
        if not self.ejected:
            os.system(f"eject {self.device}")
            self.ejected = True
    
    def notify(self, msg):
        p = subprocess.run([
            "notify-send",
            "--icon=/usr/share/icons/gnome/256x256/devices/drive-optical.png",
            "--expire-time=10000",
            "UDFBackup", msg
        ], capture_output=True)
        if p.stderr:
            logging.error(p.stderr.decode().strip())
