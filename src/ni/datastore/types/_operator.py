"""Operator data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Operator as OperatorProto,
    ExtensionValue,
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
        extensions: MutableMapping[str, ExtensionValue] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize an Operator instance."""
        self.operator_name = operator_name
        self.role = role
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(operator: OperatorProto) -> "Operator":
        """Create an Operator instance from a protobuf Operator message."""
        return Operator(
            operator_name=operator.operator_name,
            role=operator.role,
            link=operator.link,
            extensions=operator.extensions,
            schema_id=operator.schema_id,
        )

    def to_protobuf(self) -> OperatorProto:
        """Convert this Operator to a protobuf Operator message."""
        return OperatorProto(
            operator_name=self.operator_name,
            role=self.role,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

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