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


def set_logging_level(lvl: int):
    """Set logging level for all loggers in the current Python process.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    logging.getLogger(metadata.name).setLevel(lvl)
    logging.getLogger("httpx").setLevel(lvl)
    logging.getLogger("httpcore").setLevel(lvl)
