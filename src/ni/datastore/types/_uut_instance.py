"""UUT Instance data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    ExtensionValue,
    UutInstance as UutInstanceProto,
)


class UutInstance:
    """Information about a Unit Under Test (UUT) instance."""

    __slots__ = (
        "uut_id",
        "serial_number",
        "manufacture_date",
        "firmware_version",
        "hardware_version",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        uut_id: str = "",
        serial_number: str = "",
        manufacture_date: str = "",
        firmware_version: str = "",
        hardware_version: str = "",
        link: str = "",
        extensions: MutableMapping[str, ExtensionValue] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a UutInstance instance."""
        self.uut_id = uut_id
        self.serial_number = serial_number
        self.manufacture_date = manufacture_date
        self.firmware_version = firmware_version
        self.hardware_version = hardware_version
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(uut_instance: UutInstanceProto) -> "UutInstance":
        """Create a UutInstance from a protobuf UutInstance message."""
        return UutInstance(
            uut_id=uut_instance.uut_id,
            serial_number=uut_instance.serial_number,
            manufacture_date=uut_instance.manufacture_date,
            firmware_version=uut_instance.firmware_version,
            hardware_version=uut_instance.hardware_version,
            link=uut_instance.link,
            extensions=uut_instance.extensions,
            schema_id=uut_instance.schema_id,
        )

    def to_protobuf(self) -> UutInstanceProto:
        """Convert this UutInstance to a protobuf UutInstance message."""
        return UutInstanceProto(
            uut_id=self.uut_id,
            serial_number=self.serial_number,
            manufacture_date=self.manufacture_date,
            firmware_version=self.firmware_version,
            hardware_version=self.hardware_version,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, UutInstance):
            return NotImplemented
        return (
            self.uut_id == other.uut_id
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
