"""Hardware Item data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.measurements.metadata.v1.metadata_store_pb2 import (
    HardwareItem as HardwareItemProto,
    ExtensionValue,
)

class HardwareItem:
    """Information about a hardware item."""

    __slots__ = (
        "manufacturer",
        "model",
        "serial_number",
        "part_number",
        "asset_identifier",
        "calibration_due_date",
        "link",
        "extensions",
        "schema_id",
    )

    def __init__(
        self,
        *,
        manufacturer: str = "",
        model: str = "",
        serial_number: str = "",
        part_number: str = "",
        asset_identifier: str = "",
        calibration_due_date: str = "",
        link: str = "",
        extensions: MutableMapping[str, ExtensionValue] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a HardwareItem instance."""
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.part_number = part_number
        self.asset_identifier = asset_identifier
        self.calibration_due_date = calibration_due_date
        self.link = link
        self.extensions: MutableMapping[str, ExtensionValue] = (
            extensions if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(hardware_item: HardwareItemProto) -> "HardwareItem":
        """Create a HardwareItem instance from a protobuf HardwareItem message."""
        return HardwareItem(
            manufacturer=hardware_item.manufacturer,
            model=hardware_item.model,
            serial_number=hardware_item.serial_number,
            part_number=hardware_item.part_number,
            asset_identifier=hardware_item.asset_identifier,
            calibration_due_date=hardware_item.calibration_due_date,
            link=hardware_item.link,
            extensions=hardware_item.extensions,
            schema_id=hardware_item.schema_id,
        )

    def to_protobuf(self) -> HardwareItemProto:
        """Convert this HardwareItem to a protobuf HardwareItem message."""
        return HardwareItemProto(
            manufacturer=self.manufacturer,
            model=self.model,
            serial_number=self.serial_number,
            part_number=self.part_number,
            asset_identifier=self.asset_identifier,
            calibration_due_date=self.calibration_due_date,
            link=self.link,
            extensions=self.extensions,
            schema_id=self.schema_id,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, HardwareItem):
            return NotImplemented
        return (
            self.manufacturer == other.manufacturer
            and self.model == other.model
            and self.serial_number == other.serial_number
            and self.part_number == other.part_number
            and self.asset_identifier == other.asset_identifier
            and self.calibration_due_date == other.calibration_due_date
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )