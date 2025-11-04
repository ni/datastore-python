"""Tests for the ErrorInformation wrapper type."""

from __future__ import annotations

import pytest
from ni.datastore.data import ErrorInformation
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation as ErrorInformationProto,
)


def test___init___with_defaults() -> None:
    """Test creating ErrorInformation with default values."""
    error_info = ErrorInformation()

    assert error_info.error_code == 0
    assert error_info.message == ""
    assert error_info.source == ""


def test___init___with_values() -> None:
    """Test creating ErrorInformation with specific values."""
    error_info = ErrorInformation(
        error_code=42, message="Test error occurred", source="test_module.py:123"
    )

    assert error_info.error_code == 42
    assert error_info.message == "Test error occurred"
    assert error_info.source == "test_module.py:123"


def test___init___with_keyword_arguments() -> None:
    """Test creating ErrorInformation using keyword arguments in different order."""
    error_info = ErrorInformation(
        source="some_file.py", message="An error happened", error_code=404
    )

    assert error_info.error_code == 404
    assert error_info.message == "An error happened"
    assert error_info.source == "some_file.py"


def test___from_protobuf___creates_instance_from_protobuf() -> None:
    """Test creating ErrorInformation from protobuf message."""
    proto = ErrorInformationProto(error_code=123, message="Protobuf error", source="proto_source")

    error_info = ErrorInformation.from_protobuf(proto)

    assert error_info.error_code == 123
    assert error_info.message == "Protobuf error"
    assert error_info.source == "proto_source"


def test___from_protobuf___with_empty_protobuf() -> None:
    """Test creating ErrorInformation from empty protobuf message."""
    proto = ErrorInformationProto()

    error_info = ErrorInformation.from_protobuf(proto)

    assert error_info.error_code == 0
    assert error_info.message == ""
    assert error_info.source == ""


def test___to_protobuf___converts_to_protobuf_message() -> None:
    """Test converting ErrorInformation to protobuf message."""
    error_info = ErrorInformation(
        error_code=789, message="Convert this error", source="conversion_test.py"
    )

    proto = error_info.to_protobuf()

    assert isinstance(proto, ErrorInformationProto)
    assert proto.error_code == 789
    assert proto.message == "Convert this error"
    assert proto.source == "conversion_test.py"


def test___to_protobuf___with_defaults() -> None:
    """Test converting ErrorInformation with default values to protobuf."""
    error_info = ErrorInformation()

    proto = error_info.to_protobuf()

    assert isinstance(proto, ErrorInformationProto)
    assert proto.error_code == 0
    assert proto.message == ""
    assert proto.source == ""


def test___round_trip_conversion___preserves_values() -> None:
    """Test that converting to protobuf and back preserves all values."""
    original = ErrorInformation(
        error_code=555, message="Round trip test", source="round_trip.py:42"
    )

    proto = original.to_protobuf()
    converted_back = ErrorInformation.from_protobuf(proto)

    assert converted_back.error_code == original.error_code
    assert converted_back.message == original.message
    assert converted_back.source == original.source


def test___equality___same_values() -> None:
    """Test equality comparison with same values."""
    error_info1 = ErrorInformation(error_code=100, message="Same error", source="same_source.py")
    error_info2 = ErrorInformation(error_code=100, message="Same error", source="same_source.py")

    assert error_info1 == error_info2
    assert error_info2 == error_info1


def test___equality___different_values() -> None:
    """Test equality comparison with different values."""
    error_info1 = ErrorInformation(error_code=100, message="Error 1", source="source1.py")
    error_info2 = ErrorInformation(error_code=200, message="Error 2", source="source2.py")
    error_info3 = ErrorInformation(error_code=100, message="Different message", source="source1.py")
    error_info4 = ErrorInformation(error_code=100, message="Error 1", source="different_source.py")

    assert error_info1 != error_info2
    assert error_info1 != error_info3
    assert error_info1 != error_info4


def test___equality___with_defaults() -> None:
    """Test equality comparison with default values."""
    error_info1 = ErrorInformation()
    error_info2 = ErrorInformation()

    assert error_info1 == error_info2


def test___equality___with_non_error_information_object() -> None:
    """Test equality comparison with non-ErrorInformation object."""
    error_info = ErrorInformation()

    assert error_info != "not an ErrorInformation"
    assert error_info != 42
    assert error_info is not None
    assert error_info != {}


def test___str___returns_protobuf_string() -> None:
    """Test string representation returns protobuf string."""
    error_info = ErrorInformation(error_code=999, message="String test", source="str_test.py")

    str_repr = str(error_info)
    proto_str = str(error_info.to_protobuf())

    assert str_repr == proto_str
    assert "999" in str_repr
    assert "String test" in str_repr
    assert "str_test.py" in str_repr


def test___str___with_empty_values() -> None:
    """Test string representation with empty values."""
    error_info = ErrorInformation()

    str_repr = str(error_info)

    # Should be a string (may be empty for empty protobuf)
    assert isinstance(str_repr, str)
    # Should match the protobuf string representation
    assert str_repr == str(error_info.to_protobuf())


def test___slots___attribute() -> None:
    """Test that __slots__ is properly defined."""
    error_info = ErrorInformation()

    # Should have the three expected slots
    expected_slots = ("error_code", "message", "source")
    assert hasattr(ErrorInformation, "__slots__")
    assert ErrorInformation.__slots__ == expected_slots

    # Should not allow arbitrary attribute assignment
    with pytest.raises(AttributeError):
        setattr(error_info, "unexpected_attribute", "this should fail")


def test___attribute_assignment___after_initialization() -> None:
    """Test that attributes can be modified after initialization."""
    error_info = ErrorInformation(error_code=1, message="initial", source="initial.py")

    # Should be able to modify existing attributes
    error_info.error_code = 2
    error_info.message = "modified"
    error_info.source = "modified.py"

    assert error_info.error_code == 2
    assert error_info.message == "modified"
    assert error_info.source == "modified.py"
