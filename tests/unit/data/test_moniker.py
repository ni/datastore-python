"""Tests for the Moniker wrapper type."""

from __future__ import annotations

import pytest
from ni.datamonikers.v1.data_moniker_pb2 import Moniker as MonikerProto
from ni.datastore.data import Moniker


def test___init___with_defaults() -> None:
    """Test creating Moniker with default values."""
    moniker = Moniker()

    assert moniker.service_location == ""
    assert moniker.data_source == ""
    assert moniker.data_instance == 0


def test___init___with_values() -> None:
    """Test creating Moniker with specific values."""
    moniker = Moniker(
        service_location="localhost:8080", data_source="test_datasource", data_instance=42
    )

    assert moniker.service_location == "localhost:8080"
    assert moniker.data_source == "test_datasource"
    assert moniker.data_instance == 42


def test___init___with_keyword_arguments() -> None:
    """Test creating Moniker using keyword arguments in different order."""
    moniker = Moniker(
        data_instance=123, service_location="example.com:9090", data_source="my_source"
    )

    assert moniker.service_location == "example.com:9090"
    assert moniker.data_source == "my_source"
    assert moniker.data_instance == 123


def test___from_protobuf___creates_instance_from_protobuf() -> None:
    """Test creating Moniker from protobuf message."""
    proto = MonikerProto(
        service_location="proto.server:8080", data_source="proto_source", data_instance=789
    )

    moniker = Moniker.from_protobuf(proto)

    assert moniker.service_location == "proto.server:8080"
    assert moniker.data_source == "proto_source"
    assert moniker.data_instance == 789


def test___from_protobuf___with_empty_protobuf() -> None:
    """Test creating Moniker from empty protobuf message."""
    proto = MonikerProto()

    moniker = Moniker.from_protobuf(proto)

    assert moniker.service_location == ""
    assert moniker.data_source == ""
    assert moniker.data_instance == 0


def test___to_protobuf___converts_to_protobuf_message() -> None:
    """Test converting Moniker to protobuf message."""
    moniker = Moniker(
        service_location="test.service:443", data_source="test_source", data_instance=555
    )

    proto = moniker.to_protobuf()

    assert isinstance(proto, MonikerProto)
    assert proto.service_location == "test.service:443"
    assert proto.data_source == "test_source"
    assert proto.data_instance == 555


def test___to_protobuf___with_defaults() -> None:
    """Test converting Moniker with default values to protobuf."""
    moniker = Moniker()

    proto = moniker.to_protobuf()

    assert isinstance(proto, MonikerProto)
    assert proto.service_location == ""
    assert proto.data_source == ""
    assert proto.data_instance == 0


def test___round_trip_conversion___preserves_values() -> None:
    """Test that converting to protobuf and back preserves all values."""
    original = Moniker(
        service_location="roundtrip.test:8080", data_source="roundtrip_source", data_instance=999
    )

    proto = original.to_protobuf()
    converted_back = Moniker.from_protobuf(proto)

    assert converted_back.service_location == original.service_location
    assert converted_back.data_source == original.data_source
    assert converted_back.data_instance == original.data_instance


def test___equality___same_values() -> None:
    """Test equality comparison with same values."""
    moniker1 = Moniker(
        service_location="same.server:8080", data_source="same_source", data_instance=100
    )
    moniker2 = Moniker(
        service_location="same.server:8080", data_source="same_source", data_instance=100
    )

    assert moniker1 == moniker2
    assert moniker2 == moniker1


def test___equality___different_values() -> None:
    """Test equality comparison with different values."""
    moniker1 = Moniker(service_location="server1:8080", data_source="source1", data_instance=1)
    moniker2 = Moniker(service_location="server2:8080", data_source="source1", data_instance=1)
    moniker3 = Moniker(service_location="server1:8080", data_source="source2", data_instance=1)
    moniker4 = Moniker(service_location="server1:8080", data_source="source1", data_instance=2)

    assert moniker1 != moniker2
    assert moniker1 != moniker3
    assert moniker1 != moniker4


def test___equality___with_defaults() -> None:
    """Test equality comparison with default values."""
    moniker1 = Moniker()
    moniker2 = Moniker()

    assert moniker1 == moniker2


def test___equality___with_non_moniker_object() -> None:
    """Test equality comparison with non-Moniker object."""
    moniker = Moniker()

    assert moniker != "not a Moniker"
    assert moniker != 42
    assert moniker is not None
    assert moniker != {}


def test___str___returns_protobuf_string() -> None:
    """Test string representation returns protobuf string."""
    moniker = Moniker(service_location="str.test:8080", data_source="str_source", data_instance=777)

    str_repr = str(moniker)
    proto_str = str(moniker.to_protobuf())

    assert str_repr == proto_str
    assert "str.test:8080" in str_repr
    assert "str_source" in str_repr
    assert "777" in str_repr


def test___str___with_empty_values() -> None:
    """Test string representation with empty values."""
    moniker = Moniker()

    str_repr = str(moniker)

    # Should be a string (may be empty for empty protobuf)
    assert isinstance(str_repr, str)
    # Should match the protobuf string representation
    assert str_repr == str(moniker.to_protobuf())


def test___slots___attribute() -> None:
    """Test that __slots__ is properly defined."""
    moniker = Moniker()

    # Should have the three expected slots
    expected_slots = ("service_location", "data_source", "data_instance")
    assert hasattr(Moniker, "__slots__")
    assert Moniker.__slots__ == expected_slots

    # Should not allow arbitrary attribute assignment
    with pytest.raises(AttributeError):
        setattr(moniker, "unexpected_attribute", "this should fail")


def test___attribute_assignment___after_initialization() -> None:
    """Test that attributes can be modified after initialization."""
    moniker = Moniker(service_location="initial:8080", data_source="initial", data_instance=1)

    # Should be able to modify existing attributes
    moniker.service_location = "modified:9090"
    moniker.data_source = "modified"
    moniker.data_instance = 2

    assert moniker.service_location == "modified:9090"
    assert moniker.data_source == "modified"
    assert moniker.data_instance == 2


def test___data_instance___accepts_zero_and_negative_values() -> None:
    """Test that data_instance can be zero or negative."""
    moniker_zero = Moniker(data_instance=0)
    moniker_negative = Moniker(data_instance=-1)

    assert moniker_zero.data_instance == 0
    assert moniker_negative.data_instance == -1


def test___empty_strings___are_valid() -> None:
    """Test that empty strings are valid for string fields."""
    moniker = Moniker(service_location="", data_source="")

    assert moniker.service_location == ""
    assert moniker.data_source == ""

    # Should round-trip properly
    proto = moniker.to_protobuf()
    converted_back = Moniker.from_protobuf(proto)
    assert converted_back.service_location == ""
    assert converted_back.data_source == ""
