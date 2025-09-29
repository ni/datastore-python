"""Test Description data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    TestDescription as TestDescriptionProto,
)


class TestDescription:
    """Information about a test description."""

    __slots__ = (
        "uut_id",
        "test_description_name",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        uut_id: str = "",
        test_description_name: str = "",
        link: str = "",
        extensions: MutableMapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestDescription instance."""
        self.uut_id = uut_id
        self.test_description_name = test_description_name
        self.link = link
        self.extensions: MutableMapping[str, str] = extensions if extensions is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_description_proto: TestDescriptionProto) -> "TestDescription":
        """Create a TestDescription instance from a protobuf TestDescription message."""
        test_description = TestDescription(
            uut_id=test_description_proto.uut_id,
            test_description_name=test_description_proto.test_description_name,
            link=test_description_proto.link,
            schema_id=test_description_proto.schema_id,
        )
        populate_from_extension_value_message_map(
            test_description.extensions, test_description_proto.extensions
        )
        return test_description

    def to_protobuf(self) -> TestDescriptionProto:
        """Convert this TestDescription to a protobuf TestDescription message."""
        test_description_proto = TestDescriptionProto(
            uut_id=self.uut_id,
            test_description_name=self.test_description_name,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(test_description_proto.extensions, self.extensions)
        return test_description_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestDescription):
            return NotImplemented
        return (
            self.uut_id == other.uut_id
            and self.test_description_name == other.test_description_name
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the TestDescription."""
        return str(self.to_protobuf())
