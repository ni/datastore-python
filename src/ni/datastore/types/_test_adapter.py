"""Test Adapter data type for the Data Store Client."""

from __future__ import annotations

from typing import MutableMapping

from ni.datastore.grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    TestAdapter as TestAdapterProto,
)


class TestAdapter:
    """Information about a test adapter."""

    __slots__ = (
        "test_adapter_name",
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
        test_adapter_name: str = "",
        manufacturer: str = "",
        model: str = "",
        serial_number: str = "",
        part_number: str = "",
        asset_identifier: str = "",
        calibration_due_date: str = "",
        link: str = "",
        extensions: MutableMapping[str, object] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestAdapter instance."""
        self.test_adapter_name = test_adapter_name
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.part_number = part_number
        self.asset_identifier = asset_identifier
        self.calibration_due_date = calibration_due_date
        self.link = link
        self.extensions: MutableMapping[str, object] = extensions if extensions is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_adapter: TestAdapterProto) -> "TestAdapter":
        """Create a TestAdapter instance from a protobuf TestAdapter message."""
        result = TestAdapter(
            test_adapter_name=test_adapter.test_adapter_name,
            manufacturer=test_adapter.manufacturer,
            model=test_adapter.model,
            serial_number=test_adapter.serial_number,
            part_number=test_adapter.part_number,
            asset_identifier=test_adapter.asset_identifier,
            calibration_due_date=test_adapter.calibration_due_date,
            link=test_adapter.link,
            schema_id=test_adapter.schema_id,
        )
        populate_from_extension_value_message_map(result.extensions, test_adapter.extensions)
        return result

    def to_protobuf(self) -> TestAdapterProto:
        """Convert this TestAdapter to a protobuf TestAdapter message."""
        test_adapter = TestAdapterProto(
            test_adapter_name=self.test_adapter_name,
            manufacturer=self.manufacturer,
            model=self.model,
            serial_number=self.serial_number,
            part_number=self.part_number,
            asset_identifier=self.asset_identifier,
            calibration_due_date=self.calibration_due_date,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(test_adapter.extensions, self.extensions)
        return test_adapter

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestAdapter):
            return NotImplemented
        return (
            self.test_adapter_name == other.test_adapter_name
            and self.manufacturer == other.manufacturer
            and self.model == other.model
            and self.serial_number == other.serial_number
            and self.part_number == other.part_number
            and self.asset_identifier == other.asset_identifier
            and self.calibration_due_date == other.calibration_due_date
            and self.link == other.link
            and self.extensions == other.extensions
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the TestAdapter."""
        return str(self.to_protobuf())
