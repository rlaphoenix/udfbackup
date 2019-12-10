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
        s = self.__class__.__name__ + ": "
        for attr, value in self.__dict__.items():
            s = s + "(" + str(attr) + "=" + str(value) + ") "
        return s

    def load(self):
        # Make sure it's loaded and ready to go
        if self.status != self.DeviceStatus.CDS_DISC_OK:
            logging.error(f"Device {self.device} is not ready for backup, aborting. [{self.status.name}]")
            exit()
        # Get Disc Type
        context = pyudev.Context()
        device = pyudev.Devices.from_device_file(context, self.device)
        for key, value in device.items():
            if key == "ID_FS_LABEL":
                self.label = value
                if value == "iso9660":
                    self.disctype = self.DiscType.DATA
            elif key == "ID_CDROM_MEDIA_TRACK_COUNT_AUDIO":
                self.disctype = self.DiscType.CD
            elif key == "ID_CDROM_MEDIA_DVD":
                self.disctype = self.DiscType.DVD
            elif key == "ID_CDROM_MEDIA_BD":
                self.disctype = self.DiscType.BD
        logging.info(f"Initial Disc Type Analysis result: {self.disctype}")
        # Further analyse the Disc Type
        os.makedirs(str(self.mountpoint), exist_ok=True)
        os.system(f"mount {self.device}")
        if self.disctype != self.DiscType.CD:
            if os.path.isdir(os.path.join(self.mountpoint, "VIDEO_TS")):
                self.disctype = self.DiscType.DVD
            elif os.path.isdir(os.path.join(self.mountpoint, "BDMV")):
                self.disctype = self.DiscType.BD
            elif os.path.isdir(os.path.join(self.mountpoint, "HVDVD_TS")) or utils.find_file("HVDVD_TS", self.mountpoint):
                pass  # to-do ; implement this check
            else:
                # assuming generic data disc
                self.disctype = self.DiscType.DATA
        logging.info(f"Further Disc Type Analysis result: {self.disctype}")
        os.system(f"umount {self.device}")
        # Notify the user the disc state
        if self.disctype == self.DiscType.UNKNOWN:
            logging.error("Could not identify disc in {self.disc.device}, aborting.")
            exit()
        # Create a base hidden directory to indicate that it is not yet finished
        self.output_dir = os.path.join(self.base_dir, f".{self.label}_{round(time.time() * 100)}")
        utils.makedirs(self.output_dir)
        # Create a new Logger for the new log name
        self.create_logger(self.output_dir)
        # Make a log of the current object
        logging.info(self)
    
    def backup(self):
        logging.info(f"Backing up {self.disctype}")
        if self.disctype == self.DiscType.BD:
            # Get MakeMKV disc number
            mdisc = subprocess.check_output(
                args=f"makemkvcon -r info disc:9999 | grep {self.device} | grep -oP '(?<=:).*?(?=,)'",
                shell=True
            ).decode("utf-8").strip()
            # Use the Disc Number and MakeMKV's backup and decrypt feature for the disc
            subprocess.run(
                f"makemkvcon backup --decrypt -r disc:{mdisc} {shlex.quote(self.output_dir)}",
                shell=True
            )
        elif self.disctype == self.DiscType.DVD:
            # Use dvdbackup's mirror backup feature
            subprocess.run([
                "dvdbackup",
                "--input", self.device,            # choose device to dump from
                "--progress", "--verbose", "--mirror",  # show progress, be verbose, backup full disc
                "--error", "a",                         # if a read error occurs, abort
                "--output", os.path.dirname(self.output_dir),
                "--name", os.path.basename(self.output_dir)
            ], check=True)
        else:
            # to be implemented
            pass
        # Finished, let's move the directory so that it isn't in a hidden folder
        os.rename(self.output_dir, os.path.join(os.path.dirname(self.output_dir), os.path.basename[1:]))
        # Eject the finished disc
        self.eject()
    
    def create_logger(self, directory=os.path.dirname(os.path.realpath(__file__))):
        """
        Setup logging and return the path to the logfile for
        redirection of external calls
        """
        logging.basicConfig(
            #filename=os.path.join(directory, "info.log"),
            format='[%(asctime)s] %(levelname)s UDFBackup: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
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
