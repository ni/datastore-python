"""Test data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Test as TestProto,
)


class Test:
    """Information about a test."""

    __slots__ = (
        "test_name",
        "description",
        "link",
        "_extensions",
        "schema_id",
    )

    @property
    def extensions(self) -> MutableMapping[str, str]:
        """The extensions of the test."""
        return self._extensions

    def __init__(
        self,
        *,
        test_name: str = "",
        description: str = "",
        link: str = "",
        extensions: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a Test instance."""
        self.test_name = test_name
        self.description = description
        self.link = link
        self._extensions: MutableMapping[str, str] = (
            dict(extensions) if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_proto: TestProto) -> "Test":
        """Create a Test instance from a protobuf Test message."""
        test = Test(
            test_name=test_proto.test_name,
            description=test_proto.description,
            link=test_proto.link,
            schema_id=test_proto.schema_id,
        )
        populate_from_extension_value_message_map(test.extensions, test_proto.extensions)
        return test

    def to_protobuf(self) -> TestProto:
        """Convert this Test to a protobuf Test message."""
        test_proto = TestProto(
            test_name=self.test_name,
            description=self.description,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(test_proto.extensions, self.extensions)
        return test_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Test):
            return NotImplemented
        return (
            self.test_name == other.test_name
            and self.description == other.description
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Test."""
        return str(self.to_protobuf())
