# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import traceback

from typing import Union

from . import logger


def loads(s: str) -> Union[dict, list]:
    """Convert a JSON formatted string to a dict or list object

    Args:
        s (str): The JSON object represented as a string

    Returns:
        A dict or list object
    """
    try:
        return json.loads(s)
    except:
        logger.error(traceback.format_exc())
        raise
