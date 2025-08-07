# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from functools import partial

from . import metadata

def log(lvl: int, msg: str):
    """Send the log message with the specified level

    This function will send the log message to the logger with the specified
    logging level.  This function should not be direclty invoked.  Use one
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
