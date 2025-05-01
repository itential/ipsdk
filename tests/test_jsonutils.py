# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ipsdk import jsonutils


def test_loads_valid_dict():
    json_str = '{"key": "value", "number": 123}'
    result = jsonutils.loads(json_str)
    assert isinstance(result, dict)
    assert result["key"] == "value"
    assert result["number"] == 123


def test_loads_valid_list():
    json_str = '[1, 2, 3, 4]'
    result = jsonutils.loads(json_str)
    assert isinstance(result, list)
    assert result == [1, 2, 3, 4]


def test_loads_invalid_json():
    json_str = '{"key": "value", "missing_end": '
    with pytest.raises(Exception):
        jsonutils.loads(json_str)
