"""Test Adapter data type for the Data Store Client."""

from __future__ import annotations

from typing import Mapping, MutableMapping

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    TestAdapter as TestAdapterProto,
)


class TestAdapter:
    """Represents a test adapter or mechanical setup.

    This is a board or device that is used to hold, connect, or interface the
    UUT with the test system. Test adapters may also be referred to as test
    fixtures, interface boards, breakout boxes, mechanical fixtures, or
    connection adapters.

    Attributes:
        test_adapter_name: The name of the test adapter.
        manufacturer: The manufacturer of the test adapter.
        model: The model of the test adapter.
        serial_number: The serial number of the test adapter.
        part_number: The part number of the test adapter.
        asset_identifier: The asset identifier of the test adapter.
        calibration_due_date: The calibration due date of the test adapter.
        link: A link to a resource that describes the test adapter. This
            value is expected to be a valid URI.
        extensions: Any extensions to be associated with the test adapter.
        schema_id: The unique identifier of the schema that applies to this
            instance's extension. If any extension is associated with this
            instance, a schema_id must be provided, unless the test adapter
            is created within the context of a test result, in which case
            the test result must have a schema_id.
    """

    __slots__ = (
        "_id",
        "name",
        "manufacturer",
        "model",
        "serial_number",
        "part_number",
        "asset_identifier",
        "calibration_due_date",
        "link",
        "_extensions",
        "schema_id",
    )

    @property
    def extensions(self) -> MutableMapping[str, str]:
        """The extensions of the test adapter."""
        return self._extensions

    @property
    def id(self) -> str:
        """The string id of the test adapter."""
        return self._id

    def __init__(
        self,
        *,
        name: str = "",
        manufacturer: str = "",
        model: str = "",
        serial_number: str = "",
        part_number: str = "",
        asset_identifier: str = "",
        calibration_due_date: str = "",
        link: str = "",
        extensions: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a TestAdapter instance."""
        self._id = ""
        self.name = name
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.part_number = part_number
        self.asset_identifier = asset_identifier
        self.calibration_due_date = calibration_due_date
        self.link = link
        self._extensions: MutableMapping[str, str] = (
            dict(extensions) if extensions is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(test_adapter_proto: TestAdapterProto) -> "TestAdapter":
        """Create a TestAdapter instance from a protobuf TestAdapter message."""
        test_adapter = TestAdapter(
            name=test_adapter_proto.name,
            manufacturer=test_adapter_proto.manufacturer,
            model=test_adapter_proto.model,
            serial_number=test_adapter_proto.serial_number,
            part_number=test_adapter_proto.part_number,
            asset_identifier=test_adapter_proto.asset_identifier,
            calibration_due_date=test_adapter_proto.calibration_due_date,
            link=test_adapter_proto.link,
            schema_id=test_adapter_proto.schema_id,
        )
        populate_from_extension_value_message_map(
            test_adapter.extensions, test_adapter_proto.extensions
        )
        test_adapter._id = test_adapter_proto.id
        return test_adapter

    def to_protobuf(self) -> TestAdapterProto:
        """Convert this TestAdapter to a protobuf TestAdapter message."""
        test_adapter_proto = TestAdapterProto(
            id=self.id,
            name=self.name,
            manufacturer=self.manufacturer,
            model=self.model,
            serial_number=self.serial_number,
            part_number=self.part_number,
            asset_identifier=self.asset_identifier,
            calibration_due_date=self.calibration_due_date,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(test_adapter_proto.extensions, self.extensions)
        return test_adapter_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, TestAdapter):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
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
