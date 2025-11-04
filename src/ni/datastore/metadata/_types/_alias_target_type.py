"""AliasTargetType data type for the Data Store Client."""

from __future__ import annotations

from enum import IntEnum

from ni.measurements.metadata.v1.metadata_store_pb2 import AliasTargetType as AliasTargetTypeProto


class AliasTargetType(IntEnum):
    """Represents the type of target that an alias can reference.

    The AliasTargetType enum indicates what kind of metadata entity
    an alias is pointing to.
    """

    UNSPECIFIED = AliasTargetTypeProto.ALIAS_TARGET_TYPE_UNSPECIFIED
    """The alias target type is not specified or unknown."""

    UUT_INSTANCE = AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT_INSTANCE
    """The alias targets a UUT instance."""

    UUT = AliasTargetTypeProto.ALIAS_TARGET_TYPE_UUT
    """The alias targets a UUT."""

    HARDWARE_ITEM = AliasTargetTypeProto.ALIAS_TARGET_TYPE_HARDWARE_ITEM
    """The alias targets a hardware item."""

    SOFTWARE_ITEM = AliasTargetTypeProto.ALIAS_TARGET_TYPE_SOFTWARE_ITEM
    """The alias targets a software item."""

    OPERATOR = AliasTargetTypeProto.ALIAS_TARGET_TYPE_OPERATOR
    """The alias targets an operator."""

    TEST_DESCRIPTION = AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_DESCRIPTION
    """The alias targets a test description."""

    TEST = AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST
    """The alias targets a test."""

    TEST_STATION = AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_STATION
    """The alias targets a test station."""

    TEST_ADAPTER = AliasTargetTypeProto.ALIAS_TARGET_TYPE_TEST_ADAPTER
    """The alias targets a test adapter."""

    @classmethod
    def from_protobuf(cls, alias_target_type_proto: AliasTargetTypeProto.ValueType) -> "AliasTargetType":
        """Create an AliasTargetType instance from a protobuf AliasTargetType value.
        
        Args:
            alias_target_type_proto: The protobuf AliasTargetType value.
            
        Returns:
            The corresponding AliasTargetType enum value.
            
        Raises:
            ValueError: If the protobuf value doesn't correspond to a known AliasTargetType.
        """
        try:
            return cls(alias_target_type_proto)
        except ValueError as e:
            raise ValueError(f"Unknown alias target type value: {alias_target_type_proto}") from e

    def to_protobuf(self) -> AliasTargetTypeProto.ValueType:
        """Convert this AliasTargetType instance to a protobuf AliasTargetType value.
        
        Returns:
            The corresponding protobuf AliasTargetType value.
        """
        return AliasTargetTypeProto.ValueType(self.value)