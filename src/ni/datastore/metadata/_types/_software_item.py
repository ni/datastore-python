"""Software Item data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    SoftwareItem as SoftwareItemProto,
)


class SoftwareItem:
    """Represents the metadata of the software item used to take measurements.

    A software item contains information about the software product and version
    used during testing.
    """

    __slots__ = (
        "_id",
        "product",
        "version",
        "link",
        "_extension",
        "schema_id",
    )

    @property
    def extension(self) -> MutableMapping[str, str]:
        """The extension of the software item."""
        return self._extension

    @property
    def id(self) -> str:
        """The string id of the software item."""
        return self._id

    def __init__(
        self,
        *,
        product: str = "",
        version: str = "",
        link: str = "",
        extension: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a SoftwareItem instance.

        Args:
            product: The product name of the software item.
            version: The version of the software item.
            link: A link to a resource that describes the software item. This
                value is expected to be a valid URI.
            extension: Any extensions to be associated with the software item.
            schema_id: The unique identifier of the schema that applies to this
                instance's extension. If any extension is associated with this
                instance, a schema_id must be provided, unless the software item
                is created within the context of a test result, in which case
                the test result must have a schema_id.
        """
        self._id = ""
        self.product = product
        self.version = version
        self.link = link
        self._extension: MutableMapping[str, str] = dict(extension) if extension is not None else {}
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
            software_item.extension, software_item_proto.extension
        )
        software_item._id = software_item_proto.id
        return software_item

    def to_protobuf(self) -> SoftwareItemProto:
        """Convert this SoftwareItem to a protobuf SoftwareItem message."""
        software_item_proto = SoftwareItemProto(
            id=self.id,
            product=self.product,
            version=self.version,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(software_item_proto.extension, self.extension)
        return software_item_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, SoftwareItem):
            return NotImplemented
        return (
            self.id == other.id
            and self.product == other.product
            and self.version == other.version
            and self.link == other.link
            and self.extension == other.extension
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the SoftwareItem."""
        return str(self.to_protobuf())
