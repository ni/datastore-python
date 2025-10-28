"""UUT Instance data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    UutInstance as UutInstanceProto,
)


class UutInstance:
    """Represents the metadata of a UUT instance.

    A UUT instance represents a specific physical instance of a Unit Under
    Test, with properties like serial number, manufacture date, and firmware
    version that distinguish it from other instances of the same UUT model.


    """

    __slots__ = (
        "_id",
        "uut_id",
        "serial_number",
        "manufacture_date",
        "firmware_version",
        "hardware_version",
        "link",
        "_extensions",
        "schema_id",
    )

    @property
    def extensions(self) -> MutableMapping[str, str]:
        """The extensions of the UUT instance."""
        return self._extensions

    @property
    def id(self) -> str:
        """The string id of the uut instance."""
        return self._id

    def __init__(
        self,
        *,
        uut_id: str = "",
        serial_number: str = "",
        manufacture_date: str = "",
        firmware_version: str = "",
        hardware_version: str = "",
        link: str = "",
        extensions: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a UutInstance instance.

        Args:
            uut_id: The ID of the UUT associated with this UUT instance. This
                value is expected to be a parsable GUID or an alias.
            serial_number: The serial number of the UUT instance.
            manufacture_date: The date the UUT instance was manufactured.
            firmware_version: Version of the firmware on the UUT instance.
            hardware_version: Hardware version of the UUT instance.
            link: A link to a resource that describes the UUT instance. This
                value is expected to be a valid URI.
            extensions: Any extensions to be associated with the UUT instance.
            schema_id: The unique identifier of the schema that applies to this
                instance's extension. If any extension is associated with this
                instance, a schema_id must be provided, unless the UUT instance
                is created within the context of a test result, in which case
                the test result must have a schema_id.
        """
        self._id = ""
        self.uut_id = uut_id
        self.serial_number = serial_number
        self.manufacture_date = manufacture_date
        self.firmware_version = firmware_version
        self.hardware_version = hardware_version
        self.link = link
        self._extensions: MutableMapping[str, str] = (
            dict(extensions) if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(uut_instance_proto: UutInstanceProto) -> "UutInstance":
        """Create a UutInstance from a protobuf UutInstance message."""
        uut_instance = UutInstance(
            uut_id=uut_instance_proto.uut_id,
            serial_number=uut_instance_proto.serial_number,
            manufacture_date=uut_instance_proto.manufacture_date,
            firmware_version=uut_instance_proto.firmware_version,
            hardware_version=uut_instance_proto.hardware_version,
            link=uut_instance_proto.link,
            schema_id=uut_instance_proto.schema_id,
        )
        populate_from_extension_value_message_map(
            uut_instance.extensions, uut_instance_proto.extensions
        )
        uut_instance._id = uut_instance_proto.id
        return uut_instance

    def to_protobuf(self) -> UutInstanceProto:
        """Convert this UutInstance to a protobuf UutInstance message."""
        uut_instance_proto = UutInstanceProto(
            id=self.id,
            uut_id=self.uut_id,
            serial_number=self.serial_number,
            manufacture_date=self.manufacture_date,
            firmware_version=self.firmware_version,
            hardware_version=self.hardware_version,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(uut_instance_proto.extensions, self.extensions)
        return uut_instance_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, UutInstance):
            return NotImplemented
        return (
            self.id == other.id
            and self.uut_id == other.uut_id
            and self.serial_number == other.serial_number
            and self.manufacture_date == other.manufacture_date
            and self.firmware_version == other.firmware_version
            and self.hardware_version == other.hardware_version
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the UutInstance."""
        return str(self.to_protobuf())
