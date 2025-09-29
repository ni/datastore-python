"""Software Item data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    SoftwareItem as SoftwareItemProto,
)


class SoftwareItem:
    """Information about a software item."""

    __slots__ = (
        "product",
        "version",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        product: str = "",
        version: str = "",
        link: str = "",
        extensions: MutableMapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a SoftwareItem instance."""
        self.product = product
        self.version = version
        self.link = link
        self.extensions: MutableMapping[str, str] = extensions if extensions is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(software_item_proto: SoftwareItemProto) -> "SoftwareItem":
        """Create a SoftwareItem instance from a protobuf SoftwareItem message."""
        software_item = SoftwareItem(
            product=software_item_proto.product,
            version=software_item_proto.version,
            link=software_item_proto.link,
            schema_id=software_item_proto.schema_id,
        )
        populate_from_extension_value_message_map(
            software_item.extensions, software_item_proto.extensions
        )
        return software_item

    def to_protobuf(self) -> SoftwareItemProto:
        """Convert this SoftwareItem to a protobuf SoftwareItem message."""
        software_item_proto = SoftwareItemProto(
            product=self.product,
            version=self.version,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(software_item_proto.extensions, self.extensions)
        return software_item_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, SoftwareItem):
            return NotImplemented
        return (
            self.product == other.product
            and self.version == other.version
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the SoftwareItem."""
        return str(self.to_protobuf())
