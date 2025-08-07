# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import pytest

from ipsdk import jsonutils
from ipsdk import exceptions


def test_loads_valid_dict():
    """Test loading a valid JSON dict string."""
    json_str = '{"key": "value", "number": 123}'
    result = jsonutils.loads(json_str)
    assert isinstance(result, dict)
    assert result["key"] == "value"
    assert result["number"] == 123


def test_loads_valid_list():
    """Test loading a valid JSON list string."""
    json_str = '[1, 2, 3, 4]'
    result = jsonutils.loads(json_str)
    assert isinstance(result, list)
    assert result == [1, 2, 3, 4]


def test_loads_valid_nested():
    """Test loading a valid nested JSON structure."""
    json_str = '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}'
    result = jsonutils.loads(json_str)
    assert isinstance(result, dict)
    assert "users" in result
    assert len(result["users"]) == 2
    assert result["users"][0]["name"] == "Alice"


def test_loads_valid_empty():
    """Test loading valid empty JSON structures."""
    # Empty dict
    result = jsonutils.loads('{}')
    assert result == {}
    
    # Empty list
    result = jsonutils.loads('[]')
    assert result == []


def test_loads_valid_special_values():
    """Test loading JSON with special values."""
    json_str = '{"null": null, "bool": true, "number": 42.5}'
    result = jsonutils.loads(json_str)
    assert result["null"] is None
    assert result["bool"] is True
    assert result["number"] == 42.5


def test_loads_invalid_json():
    """Test loading malformed JSON raises JSONError."""
    json_str = '{"key": "value", "missing_end": '
    with pytest.raises(exceptions.JSONError) as exc_info:
        jsonutils.loads(json_str)
    
    # Check that the exception contains helpful information
    assert "Failed to parse JSON" in str(exc_info.value)
    assert "input_data" in exc_info.value.details
    assert "json_error" in exc_info.value.details


def test_loads_invalid_json_various():
    """Test various malformed JSON inputs."""
    invalid_inputs = [
        '{"unclosed": ',              # Unclosed object
        '[1, 2, 3',                   # Unclosed array
        '{"key": value}',             # Unquoted value
        '{key: "value"}',             # Unquoted key
        '{"duplicate": 1, "duplicate": 2}',  # This is actually valid JSON
        'undefined',                  # Invalid literal
        '{,}',                        # Invalid syntax
        '{"trailing": "comma",}',     # Trailing comma (invalid in JSON)
    ]
    
    for invalid_json in invalid_inputs:
        if invalid_json == '{"duplicate": 1, "duplicate": 2}':
            # This is actually valid JSON, so skip
            continue
            
        with pytest.raises(exceptions.JSONError):
            jsonutils.loads(invalid_json)


def test_loads_type_error():
    """Test loads with non-string input raises JSONError."""
    with pytest.raises(exceptions.JSONError) as exc_info:
        jsonutils.loads(123)  # type: ignore
    
    assert "Unexpected error parsing JSON" in str(exc_info.value)
    assert "original_error" in exc_info.value.details


def test_loads_none_input():
    """Test loads with None input raises JSONError."""
    with pytest.raises(exceptions.JSONError):
        jsonutils.loads(None)  # type: ignore


def test_dumps_valid_dict():
    """Test dumping a valid dict to JSON."""
    data = {"key": "value", "number": 123}
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    # Verify it can be parsed back
    parsed = json.loads(result)
    assert parsed == data


def test_dumps_valid_list():
    """Test dumping a valid list to JSON."""
    data = [1, 2, 3, 4]
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    # Verify it can be parsed back
    parsed = json.loads(result)
    assert parsed == data


def test_dumps_valid_nested():
    """Test dumping nested structures."""
    data = {
        "users": [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False}
        ],
        "total": 2,
        "metadata": None
    }
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    # Verify it can be parsed back
    parsed = json.loads(result)
    assert parsed == data


def test_dumps_valid_primitives():
    """Test dumping various primitive types."""
    test_cases = [
        {"string": "hello"},
        {"number": 42},
        {"float": 3.14},
        {"boolean": True},
        {"null": None},
        {"empty_list": []},
        {"empty_dict": {}}
    ]
    
    for data in test_cases:
        result = jsonutils.dumps(data)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data


def test_dumps_non_serializable():
    """Test dumping non-JSON-serializable objects raises JSONError."""
    class NonSerializable:
        def __init__(self):
            self.value = "test"
    
    non_serializable_obj = NonSerializable()
    with pytest.raises(exceptions.JSONError) as exc_info:
        jsonutils.dumps(non_serializable_obj)
    
    assert "Failed to serialize object to JSON" in str(exc_info.value)
    assert "object_type" in exc_info.value.details
    assert "json_error" in exc_info.value.details


def test_dumps_circular_reference():
    """Test dumping objects with circular references raises JSONError."""
    data = {"key": "value"}
    data["self"] = data  # Create circular reference
    
    with pytest.raises(exceptions.JSONError) as exc_info:
        jsonutils.dumps(data)
    
    assert "Failed to serialize object to JSON" in str(exc_info.value)
    assert "object_type" in exc_info.value.details


def test_dumps_complex_types():
    """Test dumping complex Python types that aren't JSON serializable."""
    import datetime
    import decimal
    
    non_serializable_objects = [
        datetime.datetime.now(),
        decimal.Decimal('10.5'),
        {1, 2, 3},  # set
        (1, 2, 3),  # tuple - actually this might be serializable
        bytes(b'hello'),
    ]
    
    for obj in non_serializable_objects:
        if isinstance(obj, tuple):
            # Tuples are actually serialized as arrays
            continue
            
        with pytest.raises(exceptions.JSONError):
            jsonutils.dumps(obj)


def test_error_details_truncation():
    """Test that large input data is properly truncated in error details."""
    # Create a long invalid JSON string
    long_invalid_json = '{"key": "' + 'x' * 300 + '"'  # Missing closing quote and brace
    
    with pytest.raises(exceptions.JSONError) as exc_info:
        jsonutils.loads(long_invalid_json)
    
    # Check that input_data is truncated to 200 characters
    input_data = exc_info.value.details.get("input_data", "")
    assert len(input_data) <= 200


def test_exception_inheritance():
    """Test that JSONError is properly inherited from ValidationError."""
    with pytest.raises(exceptions.ValidationError):  # Should catch JSONError
        jsonutils.loads('invalid json')
    
    with pytest.raises(exceptions.IpsdkError):  # Should catch JSONError
        jsonutils.loads('invalid json')


def test_round_trip_consistency():
    """Test that dumps -> loads produces the same data."""
    test_data = {
        "string": "hello world",
        "number": 42,
        "float": 3.14159,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3, "four", False],
        "nested": {
            "inner": "value",
            "array": [{"a": 1}, {"b": 2}]
        }
    }
    
    # dumps -> loads should preserve the data
    json_string = jsonutils.dumps(test_data)
    parsed_data = jsonutils.loads(json_string)
    
    assert parsed_data == test_data
