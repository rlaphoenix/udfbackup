#!/usr/bin/python3

import os
import sys
import logging
import subprocess
import shutil


def makedirs(path):
    """
    Make a directory\n
    path = Path to directory\n

    returns success True if successful false if the directory already exists
    """
    if os.path.exists(path):
        return False
    try:
        os.makedirs(path)
        return True
    except OSError:
        raise OSError(f"Couldn't create a directory at: `{path}` Probably a permissions error.")


def find_file(filename, search_path):
    """
    Check to see if file exists by searching a directory recursively\n
    filename = filename to look for\n
    search_path = path to search recursively\n

    returns True or False
    """

    for dirpath, dirnames, filenames in os.walk(search_path):
        if filename in filenames:
            return True
    return False


def rip_music(disc, logfile):
    """
    Rip music CD using abcde using abcde config\n
    disc = disc object\n
    logfile = location of logfile\n

    returns True/False for success/fail
    """

    if disc.disctype == "music":
        logging.info("Disc identified as music")
        cmd = 'abcde -d "{0}" >> "{1}" 2>&1'.format(
            disc.devpath,
            logfile
        )

        logging.debug("Sending command: " + cmd)

        try:
            subprocess.check_output(
                cmd,
                shell=True
            ).decode("utf-8")
            logging.info("abcde call successful")
            return True
        except subprocess.CalledProcessError as ab_error:
            err = "Call to abcde failed with code: " + str(ab_error.returncode) + "(" + str(ab_error.output) + ")"
            logging.error(err)
            # sys.exit(err)

    return False


def rip_data(disc, datapath, logfile):
    """
    Rip data disc using cat on the command line\n
    disc = disc object\n
    datapath = path to copy data to\n
    logfile = location of logfile\n

    returns True/False for success/fail
    """

    if disc.disctype == "data":
        logging.info("Disc identified as data")

        if (disc.label) == "":
            disc.label = "datadisc"

        filename = os.path.join(datapath, disc.label + ".iso")

        logging.info("Ripping data disc to: " + filename)

        cmd = 'cat "{0}" > "{1}" 2>> {2}'.format(
            disc.devpath,
            filename,
            logfile
        )

        logging.debug("Sending command: " + cmd)

        try:
            subprocess.check_output(
                cmd,
                shell=True
            ).decode("utf-8")
            logging.info("Data rip call successful")
            return True
        except subprocess.CalledProcessError as dd_error:
            err = "Data rip failed with code: " + str(dd_error.returncode) + "(" + str(dd_error.output) + ")"
            logging.error(err)
            # sys.exit(err)

    return False


def set_permissions(directory_to_traverse):
    try:
        corrected_chmod_value = int(str(cfg['CHMOD_VALUE']), 8)
        logging.info("Setting permissions to: " + str(cfg['CHMOD_VALUE']) + " on: " + directory_to_traverse)
        os.chmod(directory_to_traverse, corrected_chmod_value)

        for dirpath, l_directories, l_files in os.walk(directory_to_traverse):
            for cur_dir in l_directories:
                logging.debug("Setting path: " + cur_dir + " to permissions value: " + str(cfg['CHMOD_VALUE']))
                os.chmod(os.path.join(dirpath, cur_dir), corrected_chmod_value)
            for cur_file in l_files:
                logging.debug("Setting file: " + cur_file + " to permissions value: " + str(cfg['CHMOD_VALUE']))
                os.chmod(os.path.join(dirpath, cur_file), corrected_chmod_value)
        return True
    except Exception as e:
        err = "Permissions setting failed as: " + str(e)
        logging.error(err)
        return False
