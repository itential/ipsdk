# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Optional


def tostr(s: str) -> str:
    if s is not None:
        s = str(s)
    return s


def tobytes(s: str, encoding: str = "utf-8") -> bytes:
    """
    Convert a string into bytes using the specified encoding.

    Args:
        s (str): The input string to convert.
        encoding (str): The character encoding to use (default is 'utf-8').

    Returns:
        bytes: The encoded byte representation of the string.
    """
    return s.encode(encoding)


def toint(value: str) -> int:
    """
    Convert a string representation of an integer to an int type.

    Args:
        value (str): A string to convert

    Returns:
        int: The integer value
    """
    return int(value)


def tobool(value: Optional[str]) -> bool:
    """
    Convert a string representation of a boolean to a bool type.

    Args:
        value (Optional[str]): A string like "true", "false", "1", "0", etc.

    Returns:
        bool: The boolean value corresponding to the input.
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"true", "1", "yes", "on"}
