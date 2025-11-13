"""Operator data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Operator as OperatorProto,
)


class Operator:
    """Represents the metadata of the operator that took the test step.

    An operator contains information about the person or entity responsible for
    conducting tests, including their name and role.
    """

    __slots__ = (
        "_id",
        "name",
        "role",
        "link",
        "_extension",
        "schema_id",
    )

    @property
    def extension(self) -> MutableMapping[str, str]:
        """The extensions of the operator."""
        return self._extension

    @property
    def id(self) -> str:
        """The string id of the operator."""
        return self._id

    def __init__(
        self,
        *,
        name: str = "",
        role: str = "",
        link: str = "",
        extensions: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize an Operator instance.

        Args:
            name: The name of the operator.
            role: The role of the operator.
            link: A link to a resource that describes the operator. This value
                is expected to be a valid URI.
            extensions: Any extensions to be associated with the operator.
            schema_id: The unique identifier of the schema that applies to this
                instance's extension. If any extension is associated with this
                instance, a schema_id must be provided, unless the operator is
                created within the context of a test result, in which case the
                test result must have a schema_id.
        """
        self._id = ""
        self.name = name
        self.role = role
        self.link = link
        self._extension: MutableMapping[str, str] = (
            dict(extensions) if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(operator_proto: OperatorProto) -> "Operator":
        """Create an Operator instance from a protobuf Operator message."""
        operator = Operator(
            name=operator_proto.name,
            role=operator_proto.role,
            link=operator_proto.link,
            schema_id=operator_proto.schema_id,
        )
        populate_from_extension_value_message_map(operator.extension, operator_proto.extension)
        operator._id = operator_proto.id
        return operator

    def to_protobuf(self) -> OperatorProto:
        """Convert this Operator to a protobuf Operator message."""
        operator_proto = OperatorProto(
            id=self.id,
            name=self.name,
            role=self.role,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(operator_proto.extension, self.extension)
        return operator_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Operator):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
            and self.role == other.role
            and self.link == other.link
            and self.extension == other.extension
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Operator."""
        return str(self.to_protobuf())
