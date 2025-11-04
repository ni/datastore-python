"""Moniker data type for the Data Store Client."""

from __future__ import annotations

from ni.datamonikers.v1.data_moniker_pb2 import Moniker as MonikerProto


class Moniker:
    """Represents a data moniker for retrieving published data.

    A moniker provides the necessary information to locate and retrieve data
    from the data store, including the service location, data source, and
    data instance identifiers.
    """

    __slots__ = (
        "service_location",
        "data_source",
        "data_instance",
    )

    def __init__(
        self,
        *,
        service_location: str = "",
        data_source: str = "",
        data_instance: int = 0,
    ) -> None:
        """Initialize a Moniker instance.

        Args:
            service_location: The location of the service that stores the data.
            data_source: The identifier for the data source.
            data_instance: The instance number of the data.
        """
        self.service_location = service_location
        self.data_source = data_source
        self.data_instance = data_instance

    @staticmethod
    def from_protobuf(moniker_proto: MonikerProto) -> "Moniker":
        """Create a Moniker instance from a protobuf Moniker message."""
        return Moniker(
            service_location=moniker_proto.service_location,
            data_source=moniker_proto.data_source,
            data_instance=moniker_proto.data_instance,
        )

    def to_protobuf(self) -> MonikerProto:
        """Convert this Moniker instance to a protobuf Moniker message."""
        return MonikerProto(
            service_location=self.service_location,
            data_source=self.data_source,
            data_instance=self.data_instance,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Moniker):
            return NotImplemented
        return (
            self.service_location == other.service_location
            and self.data_source == other.data_source
            and self.data_instance == other.data_instance
        )

    def __str__(self) -> str:
        """Return a string representation of the Moniker."""
        return str(self.to_protobuf())