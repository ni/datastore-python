"""Alias data type for the Data Store Client."""

from __future__ import annotations

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Alias as AliasProto,
    AliasTargetType,
)


class Alias:
    """Information about an alias."""

    __slots__ = (
        "alias_name",
        "target_type",
        "target_id",
    )

    def __init__(
        self,
        *,
        alias_name: str = "",
        target_type: AliasTargetType.ValueType = AliasTargetType.ALIAS_TARGET_TYPE_UNSPECIFIED,
        target_id: str = "",
    ) -> None:
        """Initialize an Alias instance."""
        self.alias_name = alias_name
        self.target_type = target_type
        self.target_id = target_id

    @staticmethod
    def from_protobuf(alias_proto: AliasProto) -> "Alias":
        """Create an Alias instance from a protobuf Alias message."""
        return Alias(
            alias_name=alias_proto.alias_name,
            target_type=alias_proto.target_type,
            target_id=alias_proto.target_id,
        )

    def to_protobuf(self) -> AliasProto:
        """Convert this Alias to a protobuf Alias message."""
        return AliasProto(
            alias_name=self.alias_name,
            target_type=self.target_type,
            target_id=self.target_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Alias):
            return NotImplemented
        return (
            self.alias_name == other.alias_name
            and self.target_type == other.target_type
            and self.target_id == other.target_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Alias."""
        return str(self.to_protobuf())
