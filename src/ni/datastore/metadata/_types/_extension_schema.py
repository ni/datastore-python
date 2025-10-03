"""Extension Schema data type for the Data Store Client."""

from __future__ import annotations

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    ExtensionSchema as ExtensionSchemaProto,
)


class ExtensionSchema:
    """Information about an extension schema."""

    __slots__ = (
        "schema_id",
        "schema",
    )

    def __init__(
        self,
        *,
        schema_id: str = "",
        schema: str = "",
    ) -> None:
        """Initialize an ExtensionSchema instance."""
        self.schema_id = schema_id
        self.schema = schema

    @staticmethod
    def from_protobuf(extension_schema_proto: ExtensionSchemaProto) -> "ExtensionSchema":
        """Create an ExtensionSchema instance from a protobuf ExtensionSchema message."""
        return ExtensionSchema(
            schema_id=extension_schema_proto.schema_id,
            schema=extension_schema_proto.schema,
        )

    def to_protobuf(self) -> ExtensionSchemaProto:
        """Convert this ExtensionSchema to a protobuf ExtensionSchema message."""
        return ExtensionSchemaProto(
            schema_id=self.schema_id,
            schema=self.schema,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, ExtensionSchema):
            return NotImplemented
        return self.schema_id == other.schema_id and self.schema == other.schema

    def __str__(self) -> str:
        """Return a string representation of the ExtensionSchema."""
        return str(self.to_protobuf())
