# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from .client import platform, gateway, cloud

__all__ = [platform, gateway, cloud]

# Configure global logging
logging_message_format = '%(asctime)s: %(levelname)s: %(message)s'
logging.basicConfig(format=logging_message_format)
logging.getLogger("ipsdk").setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

def set_logging_level(lvl: int):
    """
    Set logging level for all loggers in the current Python process.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    logging.getLogger("ipsdk").setLevel(lvl)
