"""Tests for the AliasTargetType wrapper enum."""

from __future__ import annotations

from typing import cast

import pytest
from ni.datastore.metadata import AliasTargetType
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    AliasTargetType as AliasTargetTypeProto,
)


def test___enum_values___match_protobuf_values() -> None:
    """Test that enum values match the protobuf enum values."""
    assert AliasTargetType.UNSPECIFIED == AliasTargetTypeProto.ALIAS_TARGET_TYPE_UNSPECIFIED
    assert AliasTargetType.UUT_INSTANCE == AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT_INSTANCE
    assert AliasTargetType.UUT == AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT
    assert AliasTargetType.HARDWARE_ITEM == AliasTargetTypeProto.ALIAS_TARGET_TYPE_HARDWARE_ITEM
    assert AliasTargetType.SOFTWARE_ITEM == AliasTargetTypeProto.ALIAS_TARGET_TYPE_SOFTWARE_ITEM
    assert AliasTargetType.OPERATOR == AliasTargetTypeProto.ALIAS_TARGET_TYPE_OPERATOR
    assert (
        AliasTargetType.TEST_DESCRIPTION == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_DESCRIPTION
    )
    assert AliasTargetType.TEST == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST
    assert AliasTargetType.TEST_STATION == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_STATION
    assert AliasTargetType.TEST_ADAPTER == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_ADAPTER


def test___enum_values___have_expected_integer_values() -> None:
    """Test that enum has the expected integer values."""
    assert AliasTargetType.UNSPECIFIED == 0
    assert AliasTargetType.UUT_INSTANCE == 1
    assert AliasTargetType.UUT == 2
    assert AliasTargetType.HARDWARE_ITEM == 3
    assert AliasTargetType.SOFTWARE_ITEM == 4
    assert AliasTargetType.OPERATOR == 5
    assert AliasTargetType.TEST_DESCRIPTION == 6
    assert AliasTargetType.TEST == 7
    assert AliasTargetType.TEST_STATION == 8
    assert AliasTargetType.TEST_ADAPTER == 9


def test___to_protobuf___converts_enum_to_protobuf_value() -> None:
    """Test converting enum to protobuf value."""
    assert (
        AliasTargetType.UNSPECIFIED.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_UNSPECIFIED
    )
    assert (
        AliasTargetType.UUT_INSTANCE.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT_INSTANCE
    )
    assert AliasTargetType.UUT.to_protobuf() == AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT
    assert (
        AliasTargetType.HARDWARE_ITEM.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_HARDWARE_ITEM
    )
    assert (
        AliasTargetType.SOFTWARE_ITEM.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_SOFTWARE_ITEM
    )
    assert AliasTargetType.OPERATOR.to_protobuf() == AliasTargetTypeProto.ALIAS_TARGET_TYPE_OPERATOR
    assert (
        AliasTargetType.TEST_DESCRIPTION.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_DESCRIPTION
    )
    assert AliasTargetType.TEST.to_protobuf() == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST
    assert (
        AliasTargetType.TEST_STATION.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_STATION
    )
    assert (
        AliasTargetType.TEST_ADAPTER.to_protobuf()
        == AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_ADAPTER
    )


def test___from_protobuf___converts_protobuf_value_to_enum() -> None:
    """Test converting protobuf value to enum."""
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_UNSPECIFIED)
        == AliasTargetType.UNSPECIFIED
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT_INSTANCE)
        == AliasTargetType.UUT_INSTANCE
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT)
        == AliasTargetType.UUT
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_HARDWARE_ITEM)
        == AliasTargetType.HARDWARE_ITEM
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_SOFTWARE_ITEM)
        == AliasTargetType.SOFTWARE_ITEM
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_OPERATOR)
        == AliasTargetType.OPERATOR
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_DESCRIPTION)
        == AliasTargetType.TEST_DESCRIPTION
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST)
        == AliasTargetType.TEST
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_STATION)
        == AliasTargetType.TEST_STATION
    )
    assert (
        AliasTargetType.from_protobuf(AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_ADAPTER)
        == AliasTargetType.TEST_ADAPTER
    )


def test___round_trip_conversion___preserves_enum_value() -> None:
    """Test that converting to protobuf and back gives the same result."""
    for alias_target_type in AliasTargetType:
        pb_alias_target_type = alias_target_type.to_protobuf()
        back_to_enum = AliasTargetType.from_protobuf(pb_alias_target_type)
        assert alias_target_type == back_to_enum


def test___invalid_value___from_protobuf___raises_value_error() -> None:
    """Test that from_protobuf raises ValueError for invalid values."""
    with pytest.raises(ValueError, match="Unknown alias target type value"):
        AliasTargetType.from_protobuf(cast(AliasTargetTypeProto.ValueType, 999))


def test___enum___is_iterable() -> None:
    """Test that the enum can be iterated over."""
    alias_target_types = list(AliasTargetType)
    assert len(alias_target_types) == 10
    assert AliasTargetType.UNSPECIFIED in alias_target_types
    assert AliasTargetType.UUT_INSTANCE in alias_target_types
    assert AliasTargetType.UUT in alias_target_types
    assert AliasTargetType.HARDWARE_ITEM in alias_target_types
    assert AliasTargetType.SOFTWARE_ITEM in alias_target_types
    assert AliasTargetType.OPERATOR in alias_target_types
    assert AliasTargetType.TEST_DESCRIPTION in alias_target_types
    assert AliasTargetType.TEST in alias_target_types
    assert AliasTargetType.TEST_STATION in alias_target_types
    assert AliasTargetType.TEST_ADAPTER in alias_target_types


def test___enum___has_correct_name_and_value_attributes() -> None:
    """Test that enum has correct name and value attributes."""
    assert AliasTargetType.UUT_INSTANCE.name == "UUT_INSTANCE"
    assert AliasTargetType.UUT_INSTANCE.value == 1
    assert AliasTargetType.TEST.name == "TEST"
    assert AliasTargetType.TEST.value == 7
    assert AliasTargetType.TEST_ADAPTER.name == "TEST_ADAPTER"
    assert AliasTargetType.TEST_ADAPTER.value == 9


def test___enum___supports_comparison() -> None:
    """Test that enum supports comparison operations."""
    assert AliasTargetType.UNSPECIFIED < AliasTargetType.UUT_INSTANCE
    assert AliasTargetType.UUT_INSTANCE <= AliasTargetType.UUT_INSTANCE
    assert AliasTargetType.UUT_INSTANCE <= AliasTargetType.UUT
    assert AliasTargetType.TEST_ADAPTER > AliasTargetType.TEST_STATION
    assert AliasTargetType.TEST_ADAPTER >= AliasTargetType.TEST_STATION
    assert AliasTargetType.TEST_ADAPTER >= AliasTargetType.TEST_ADAPTER


def test___enum___supports_integer_operations() -> None:
    """Test that enum supports integer operations since it inherits from IntEnum."""
    # Can be used as integers
    assert AliasTargetType.UNSPECIFIED + 1 == 1
    assert AliasTargetType.UUT_INSTANCE * 2 == 2
    assert AliasTargetType.TEST - 1 == 6

    # Can be compared with integers
    assert AliasTargetType.UNSPECIFIED == 0
    assert AliasTargetType.TEST_ADAPTER == 9

    # Can be used in arithmetic contexts
    values = [AliasTargetType.UNSPECIFIED, AliasTargetType.UUT_INSTANCE, AliasTargetType.UUT]
    assert sum(values) == 3  # 0 + 1 + 2
