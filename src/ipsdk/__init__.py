# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from . import metadata

from .platform import platform_factory
from .gateway import gateway_factory

__version__ = metadata.version

__all__ = (platform_factory, gateway_factory)


# Configure global logging
logging_message_format = "%(asctime)s: %(levelname)s: %(message)s"
logging.basicConfig(format=logging_message_format)
logging.getLogger(metadata.name).setLevel(100)


def set_logging_level(lvl: int, propagate: bool=False) -> None:
    """Set logging level for all loggers in the current Python process.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).  This
            is a required argument

        propagate (bool): Setting this value to True will also turn on
            logging for httpx and httpcore.
    """
    logging.getLogger(metadata.name).setLevel(lvl)

    if propagate is True:
        logging.getLogger("httpx").setLevel(lvl)
        logging.getLogger("httpcore").setLevel(lvl)

    logging.getLogger(metadata.name).log(logging.INFO, f"ipsdk version {metadata.version}")
    logging.getLogger(metadata.name).log(logging.INFO, f"Logging level set to {lvl}")
    logging.getLogger(metadata.name).log(logging.INFO, f"Logging propagation is {propagate}")
