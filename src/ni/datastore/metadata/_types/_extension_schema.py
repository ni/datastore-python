"""Extension Schema data type for the Data Store Client."""

from __future__ import annotations

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    ExtensionSchema as ExtensionSchemaProto,
)


class ExtensionSchema:
    """Represents an extension schema stored in the system.

    An extension schema contains the schema ID and the schema definition
    itself, which can be used to validate extension data in metadata instances.
    """

    __slots__ = (
        "id",
        "schema",
    )

    def __init__(
        self,
        *,
        id: str = "",
        schema: str = "",
    ) -> None:
        """Initialize an ExtensionSchema instance.

        Args:
            id: The ID of the schema.
            schema: The schema itself.
        """
        self.id = id
        self.schema = schema

    @staticmethod
    def from_protobuf(extension_schema_proto: ExtensionSchemaProto) -> "ExtensionSchema":
        """Create an ExtensionSchema instance from a protobuf ExtensionSchema message."""
        return ExtensionSchema(
            id=extension_schema_proto.id,
            schema=extension_schema_proto.schema,
        )

    def to_protobuf(self) -> ExtensionSchemaProto:
        """Convert this ExtensionSchema to a protobuf ExtensionSchema message."""
        return ExtensionSchemaProto(
            id=self.id,
            schema=self.schema,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, ExtensionSchema):
            return NotImplemented
        return self.id == other.id and self.schema == other.schema

    def __str__(self) -> str:
        """Return a string representation of the ExtensionSchema."""
        return str(self.to_protobuf())
