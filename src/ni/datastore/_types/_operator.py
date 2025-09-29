"""Operator data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Operator as OperatorProto,
)


class Operator:
    """Information about an operator."""

    __slots__ = (
        "operator_name",
        "role",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        operator_name: str = "",
        role: str = "",
        link: str = "",
        extensions: MutableMapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize an Operator instance."""
        self.operator_name = operator_name
        self.role = role
        self.link = link
        self.extensions: MutableMapping[str, str] = extensions if extensions is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(operator_proto: OperatorProto) -> "Operator":
        """Create an Operator instance from a protobuf Operator message."""
        operator = Operator(
            operator_name=operator_proto.operator_name,
            role=operator_proto.role,
            link=operator_proto.link,
            schema_id=operator_proto.schema_id,
        )
        populate_from_extension_value_message_map(operator.extensions, operator_proto.extensions)
        return operator

    def to_protobuf(self) -> OperatorProto:
        """Convert this Operator to a protobuf Operator message."""
        operator_proto = OperatorProto(
            operator_name=self.operator_name,
            role=self.role,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(operator_proto.extensions, self.extensions)
        return operator_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Operator):
            return NotImplemented
        return (
            self.operator_name == other.operator_name
            and self.role == other.role
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Operator."""
        return str(self.to_protobuf())
