"""Test Description data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    TestDescription as TestDescriptionProto,
)


class TestDescription:
    """Represents the metadata of a test description.

    A test description contains information about a test procedure designed for
    a specific UUT, including the UUT ID and test description name.
    """

    __slots__ = (
        "_id",
        "uut_id",
        "name",
        "link",
        "_extension",
        "schema_id",
    )

    @property
    def extension(self) -> MutableMapping[str, str]:
        """The extension of the test description."""
        return self._extension

    @property
    def id(self) -> str:
        """The string id of the test description."""
        return self._id

    def __init__(
        self,
        *,
        uut_id: str = "",
        name: str = "",
        link: str = "",
        extension: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestDescription instance.

        Args:
            uut_id: The ID of the UUT associated with this test description.
                This value is expected to be a parsable GUID or an alias.
            name: The name of the test description.
            link: A link to a resource that describes the test description. This
                value is expected to be a valid URI.
            extension: Any extensions to be associated with the test description.
            schema_id: The unique identifier of the schema that applies to this
                instance's extension. If any extension is associated with this
                instance, a schema_id must be provided, unless the test description
                is created within the context of a test result, in which case
                the test result must have a schema_id.
        """
        self._id = ""
        self.uut_id = uut_id
        self.name = name
        self.link = link
        self._extension: MutableMapping[str, str] = dict(extension) if extension is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_description_proto: TestDescriptionProto) -> "TestDescription":
        """Create a TestDescription instance from a protobuf TestDescription message."""
        test_description = TestDescription(
            uut_id=test_description_proto.uut_id,
            name=test_description_proto.name,
            link=test_description_proto.link,
            schema_id=test_description_proto.schema_id,
        )
        populate_from_extension_value_message_map(
            test_description.extension, test_description_proto.extension
        )
        test_description._id = test_description_proto.id
        return test_description

    def to_protobuf(self) -> TestDescriptionProto:
        """Convert this TestDescription to a protobuf TestDescription message."""
        test_description_proto = TestDescriptionProto(
            id=self.id,
            uut_id=self.uut_id,
            name=self.name,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(test_description_proto.extension, self.extension)
        return test_description_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestDescription):
            return NotImplemented
        return (
            self.id == other.id
            and self.uut_id == other.uut_id
            and self.name == other.name
            and self.link == other.link
            and self.extension == other.extension
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the TestDescription."""
        return str(self.to_protobuf())
