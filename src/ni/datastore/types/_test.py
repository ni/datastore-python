"""Test data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    ExtensionValue,
    Test as TestProto,
)


class Test:
    """Information about a test."""

    __slots__ = (
        "test_name",
        "description",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        test_name: str = "",
        description: str = "",
        link: str = "",
        extensions: MutableMapping[str, ExtensionValue] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a Test instance."""
        self.test_name = test_name
        self.description = description
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test: TestProto) -> "Test":
        """Create a Test instance from a protobuf Test message."""
        return Test(
            test_name=test.test_name,
            description=test.description,
            link=test.link,
            extensions=test.extensions,
            schema_id=test.schema_id,
        )

    def to_protobuf(self) -> TestProto:
        """Convert this Test to a protobuf Test message."""
        return TestProto(
            test_name=self.test_name,
            description=self.description,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

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
