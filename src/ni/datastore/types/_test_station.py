"""Test Station data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    TestStation as TestStationProto,
    ExtensionValue,
)

class TestStation:
    """Information about a test station."""

    __slots__ = (
        "test_station_name",
        "asset_identifier",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        test_station_name: str = "",
        asset_identifier: str = "",
        link: str = "",
        extensions: MutableMapping[str, ExtensionValue] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestStation instance."""
        self.test_station_name = test_station_name
        self.asset_identifier = asset_identifier
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_station: TestStationProto) -> "TestStation":
        """Create a TestStation instance from a protobuf TestStation message."""
        return TestStation(
            test_station_name=test_station.test_station_name,
            asset_identifier=test_station.asset_identifier,
            link=test_station.link,
            extensions=test_station.extensions,
            schema_id=test_station.schema_id,
        )

    def to_protobuf(self) -> TestStationProto:
        """Convert this TestStation to a protobuf TestStation message."""
        return TestStationProto(
            test_station_name=self.test_station_name,
            asset_identifier=self.asset_identifier,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestStation):
            return NotImplemented
        return (
            self.test_station_name == other.test_station_name
            and self.asset_identifier == other.asset_identifier
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )