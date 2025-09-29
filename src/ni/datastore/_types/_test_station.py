"""Test Station data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    TestStation as TestStationProto,
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
        extensions: MutableMapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestStation instance."""
        self.test_station_name = test_station_name
        self.asset_identifier = asset_identifier
        self.link = link
        self.extensions: MutableMapping[str, str] = extensions if extensions is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_station_proto: TestStationProto) -> "TestStation":
        """Create a TestStation instance from a protobuf TestStation message."""
        test_station = TestStation(
            test_station_name=test_station_proto.test_station_name,
            asset_identifier=test_station_proto.asset_identifier,
            link=test_station_proto.link,
            schema_id=test_station_proto.schema_id,
        )
        populate_from_extension_value_message_map(
            test_station.extensions, test_station_proto.extensions
        )
        return test_station

    def to_protobuf(self) -> TestStationProto:
        """Convert this TestStation to a protobuf TestStation message."""
        test_station_proto = TestStationProto(
            test_station_name=self.test_station_name,
            asset_identifier=self.asset_identifier,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(test_station_proto.extensions, self.extensions)
        return test_station_proto

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

    def __str__(self) -> str:
        """Return a string representation of the TestStation."""
        return str(self.to_protobuf())
