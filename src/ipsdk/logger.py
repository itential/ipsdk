# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import logging

from functools import partial

from . import metadata

# Configure global logging
logging_message_format = "%(asctime)s: %(levelname)s: %(message)s"
logging.basicConfig(format=logging_message_format)
logging.getLogger(metadata.name).setLevel(100)

# Add the FATAL logging level
logging.addLevelName(90, "FATAL")
setattr(logging, "FATAL", 90)

# Logging level constants that wrap stdlib logging module constants
NOTSET = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL

# Set the default logging level to 100
logging.getLogger(metadata.name).setLevel(100)


def log(lvl: int, msg: str) -> None:
    """Send the log message with the specified level

    This function will send the log message to the logger with the specified
    logging level.  This function should not be directly invoked.  Use one
    of the partials to send a log message with a given level.

    Args:
        lvl (int): The logging level of the message
        msg (str): The message to write to the logger
    """
    logging.getLogger(metadata.name).log(lvl, msg)


debug = partial(log, logging.DEBUG)
info = partial(log, logging.INFO)
warning = partial(log, logging.WARNING)
error = partial(log, logging.ERROR)
critical = partial(log, logging.CRITICAL)


def exception(exc: Exception) -> None:
    """
    Log an exception error

    Args:
        exc (Exception): Exception to log as an error

    Returns:
        None
    """
    log(logging.ERROR, str(exc))


def fatal(msg: str) -> None:
    """
    Log a fatal error

    A fatal error will log the message using level 90 (FATAL) and print
    an error message to stdout.  It will then exit the application with
    return code 1

    Args:
        msg (str): The message to print

    Returns:
        None

    Raises:
        None
    """
    log(logging.FATAL, msg)
    print(f"ERROR: {msg}")
    sys.exit(1)


def set_level(lvl: int, propagate: bool=False) -> None:
    """Set logging level for all loggers in the current Python process.

    Args:
        lvl (int): Logging level (e.g., logging.INFO, logging.DEBUG).  This
            is a required argument

        propagate (bool): Setting this value to True will also turn on
            logging for httpx and httpcore.

    Returns:
        None

    Raises:
        None
    """
    logging.getLogger(metadata.name).setLevel(lvl)

    if propagate is True:
        logging.getLogger("httpx").setLevel(lvl)
        logging.getLogger("httpcore").setLevel(lvl)

    logging.getLogger(metadata.name).log(logging.INFO, f"ipsdk version {metadata.version}")
    logging.getLogger(metadata.name).log(logging.INFO, f"Logging level set to {lvl}")
    logging.getLogger(metadata.name).log(logging.INFO, f"Logging propagation is {propagate}")
