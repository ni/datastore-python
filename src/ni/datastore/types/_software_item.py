"""Software Item data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    ExtensionValue,
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
        extensions: MutableMapping[str, ExtensionValue] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a SoftwareItem instance."""
        self.product = product
        self.version = version
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(software_item: SoftwareItemProto) -> "SoftwareItem":
        """Create a SoftwareItem instance from a protobuf SoftwareItem message."""
        return SoftwareItem(
            product=software_item.product,
            version=software_item.version,
            link=software_item.link,
            extensions=software_item.extensions,
            schema_id=software_item.schema_id,
        )

    def to_protobuf(self) -> SoftwareItemProto:
        """Convert this SoftwareItem to a protobuf SoftwareItem message."""
        return SoftwareItemProto(
            product=self.product,
            version=self.version,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

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
