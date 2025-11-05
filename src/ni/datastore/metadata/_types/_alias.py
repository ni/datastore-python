"""Alias data type for the Data Store Client."""

from __future__ import annotations

from ni.measurements.metadata.v1.metadata_store_pb2 import Alias as AliasProto

from ._alias_target_type import AliasTargetType


class Alias:
    """Represents an alias for metadata.

    An alias provides a user-friendly name that maps to a specific metadata
    instance, containing the alias name, the type of the aliased metadata
    instance, and the unique identifier for the aliased metadata instance.
    """

    __slots__ = (
        "name",
        "target_type",
        "target_id",
    )

    def __init__(
        self,
        *,
        name: str = "",
        target_type: AliasTargetType = AliasTargetType.UNSPECIFIED,
        target_id: str = "",
    ) -> None:
        """Initialize an Alias instance.

        Args:
            name: The registered alias name for the aliased metadata
                instance.
            target_type: The type of the aliased metadata instance.
            target_id: The unique identifier for the aliased metadata instance.
        """
        self.name = name
        self.target_type = target_type
        self.target_id = target_id

    @staticmethod
    def from_protobuf(alias_proto: AliasProto) -> "Alias":
        """Create an Alias instance from a protobuf Alias message."""
        return Alias(
            name=alias_proto.name,
            target_type=AliasTargetType.from_protobuf(alias_proto.target_type),
            target_id=alias_proto.target_id,
        )

    def to_protobuf(self) -> AliasProto:
        """Convert this Alias to a protobuf Alias message."""
        return AliasProto(
            name=self.name,
            target_type=self.target_type.to_protobuf(),
            target_id=self.target_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Alias):
            return NotImplemented
        return (
            self.name == other.name
            and self.target_type == other.target_type
            and self.target_id == other.target_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Alias."""
        return str(self.to_protobuf())
