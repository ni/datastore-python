"""Measurement data type for the V2 Data Store Client."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, MutableMapping, MutableSequence, Sequence

import hightime as ht
from ni.measurements.data.v2.data_store_pb2 import Measurement as MeasurementProto
from nitypes.scalar import Scalar

from ni.datastore.data.v2._grpc_conversion import (
    duration_from_protobuf,
    duration_to_protobuf,
    extension_from_protobuf,
    extension_to_protobuf,
    measurement_value_from_protobuf,
    measurement_value_to_protobuf,
    timestamp_from_protobuf,
    timestamp_to_protobuf,
)
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.metadata import HardwareItem, SoftwareItem, TestAdapter


class Measurement:
    """A measurement stored in the data store.

    The value and limits are sent on create. Reads return them only when the
    service includes an inline value; use DataStoreClient.read_measurement_value
    or DataStoreClient.read_measurement_values to read them reliably.
    """

    __slots__ = (
        "id",
        "test_result_id",
        "step_id",
        "name",
        "value",
        "upper_limit",
        "lower_limit",
        "value_type",
        "units",
        "notes",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "error_information",
        "_extension",
        "schema_id",
        "_software_item_ids",
        "_hardware_item_ids",
        "_test_adapter_ids",
        "_software_items",
        "_hardware_items",
        "_test_adapters",
        "comparison_type",
        "_conditions",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    @property
    def extension(self) -> MutableMapping[str, Any]:
        """Custom JSON data associated with the measurement."""
        return self._extension

    @property
    def software_item_ids(self) -> MutableSequence[str]:
        """The software item IDs associated with the measurement."""
        return self._software_item_ids

    @property
    def hardware_item_ids(self) -> MutableSequence[str]:
        """The hardware item IDs associated with the measurement."""
        return self._hardware_item_ids

    @property
    def test_adapter_ids(self) -> MutableSequence[str]:
        """The test adapter IDs associated with the measurement."""
        return self._test_adapter_ids

    @property
    def software_items(self) -> MutableSequence[SoftwareItem]:
        """Software items to find or create on create, or expand on read."""
        return self._software_items

    @property
    def hardware_items(self) -> MutableSequence[HardwareItem]:
        """Hardware items to find or create on create, or expand on read."""
        return self._hardware_items

    @property
    def test_adapters(self) -> MutableSequence[TestAdapter]:
        """Test adapters to find or create on create, or expand on read."""
        return self._test_adapters

    @property
    def conditions(self) -> Sequence[Condition]:
        """Read-only output-only conditions copied from the owning step."""
        return self._conditions

    def __init__(
        self,
        *,
        id: str = "",
        test_result_id: str = "",
        step_id: str = "",
        name: str = "",
        value: object = None,
        upper_limit: object = None,
        lower_limit: object = None,
        value_type: str = "",
        units: str = "",
        notes: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        duration: ht.timedelta | None = None,
        outcome: Outcome = Outcome.UNSPECIFIED,
        error_information: ErrorInformation | None = None,
        extension: Mapping[str, Any] | None = None,
        schema_id: str = "",
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        software_items: Iterable[SoftwareItem] | None = None,
        hardware_items: Iterable[HardwareItem] | None = None,
        test_adapters: Iterable[TestAdapter] | None = None,
        comparison_type: str = "",
        conditions: Iterable[Condition] | None = None,
        created_at: ht.datetime | None = None,
        updated_at: ht.datetime | None = None,
        created_by: str = "",
        updated_by: str = "",
    ) -> None:
        """Initialize a Measurement instance.

        Output-only fields are accepted so a Measurement can represent a service
        response. They are not included in protobuf requests. Update conditions by
        calling DataStoreClient.add_condition or remove_condition on the owning step.

        Args:
            id (optional): Unique identifier of the measurement.
            test_result_id (optional): ID of the test result the measurement belongs to.
            step_id (optional): ID of the step the measurement belongs to.
            name (optional): The name of the measurement.
            value (optional): The measured value. See DataStoreClient.create_measurement
                for the supported types.
            upper_limit (optional): The publisher-supplied upper limit. Any value type
                supported for value is accepted. The service stores it but does not
                compare it with the value.
            lower_limit (optional): The publisher-supplied lower limit. Any value type
                supported for value is accepted. The service stores it but does not
                compare it with the value.
            value_type (optional): Output only. The service-generated value type.
            units (optional): Engineering units of the value. Defaults to the units of a
                Scalar value.
            notes (optional): Additional notes about the measurement.
            start_date_time (optional): The start date and time of the measurement.
            end_date_time (optional): The end date and time of the measurement.
            duration (optional): The duration of the measurement.
            outcome (optional): The outcome of the measurement.
            error_information (optional): Error details for the measurement.
            extension (optional): Custom JSON data for the measurement.
            schema_id (optional): Schema that governs the extension. Reserved for
                future use.
            software_item_ids (optional): IDs of software items used for the measurement.
            hardware_item_ids (optional): IDs of hardware items used for the measurement.
            test_adapter_ids (optional): IDs of test adapters used for the measurement.
            software_items (optional): Software items to find or create on create. Each
                item must already be linked to the owning test result.
            hardware_items (optional): Hardware items to find or create on create. Each
                item must already be linked to the owning test result.
            test_adapters (optional): Test adapters to find or create on create. Each
                item must already be linked to the owning test result.
            comparison_type (optional): The publisher-defined comparison operation.
            conditions (optional): Output only. Read-only conditions copied from the
                owning step.
            created_at (optional): Output only. When the measurement was created.
            updated_at (optional): Output only. When the measurement was last updated.
            created_by (optional): Output only. Who created the measurement.
            updated_by (optional): Output only. Who last updated the measurement.
        """
        self.id = id
        self.test_result_id = test_result_id
        self.step_id = step_id
        self.name = name
        self.value = value
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.value_type = value_type
        self.units = units
        self.notes = notes
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.duration = duration
        self.outcome = outcome
        self.error_information = error_information
        self._extension: MutableMapping[str, Any] = dict(extension) if extension is not None else {}
        self.schema_id = schema_id
        self._software_item_ids: MutableSequence[str] = (
            list(software_item_ids) if software_item_ids is not None else []
        )
        self._hardware_item_ids: MutableSequence[str] = (
            list(hardware_item_ids) if hardware_item_ids is not None else []
        )
        self._test_adapter_ids: MutableSequence[str] = (
            list(test_adapter_ids) if test_adapter_ids is not None else []
        )
        self._software_items: MutableSequence[SoftwareItem] = (
            list(software_items) if software_items is not None else []
        )
        self._hardware_items: MutableSequence[HardwareItem] = (
            list(hardware_items) if hardware_items is not None else []
        )
        self._test_adapters: MutableSequence[TestAdapter] = (
            list(test_adapters) if test_adapters is not None else []
        )
        self.comparison_type = comparison_type
        self._conditions: tuple[Condition, ...] = (
            tuple(conditions) if conditions is not None else ()
        )
        self.created_at = created_at
        self.updated_at = updated_at
        self.created_by = created_by
        self.updated_by = updated_by

    @staticmethod
    def from_protobuf(measurement_proto: MeasurementProto) -> "Measurement":
        """Create a Measurement instance from a protobuf Measurement message."""
        return Measurement(
            id=measurement_proto.id,
            test_result_id=measurement_proto.test_result_id,
            step_id=measurement_proto.step_id,
            name=measurement_proto.name,
            value=measurement_value_from_protobuf(measurement_proto, "value"),
            upper_limit=measurement_value_from_protobuf(measurement_proto, "upper_limit"),
            lower_limit=measurement_value_from_protobuf(measurement_proto, "lower_limit"),
            value_type=measurement_proto.value_type,
            units=measurement_proto.units,
            notes=measurement_proto.notes,
            start_date_time=timestamp_from_protobuf(measurement_proto, "start_date_time"),
            end_date_time=timestamp_from_protobuf(measurement_proto, "end_date_time"),
            duration=duration_from_protobuf(measurement_proto, "duration"),
            outcome=Outcome.from_protobuf(measurement_proto.outcome),
            error_information=(
                ErrorInformation.from_protobuf(measurement_proto.error_information)
                if measurement_proto.HasField("error_information")
                else None
            ),
            extension=extension_from_protobuf(measurement_proto.extension),
            schema_id=measurement_proto.schema_id,
            software_item_ids=measurement_proto.software_item_ids,
            hardware_item_ids=measurement_proto.hardware_item_ids,
            test_adapter_ids=measurement_proto.test_adapter_ids,
            software_items=[
                SoftwareItem.from_protobuf(item) for item in measurement_proto.software_items
            ],
            hardware_items=[
                HardwareItem.from_protobuf(item) for item in measurement_proto.hardware_items
            ],
            test_adapters=[
                TestAdapter.from_protobuf(adapter) for adapter in measurement_proto.test_adapters
            ],
            comparison_type=measurement_proto.comparison_type,
            conditions=[
                Condition.from_protobuf(condition) for condition in measurement_proto.conditions
            ],
            created_at=timestamp_from_protobuf(measurement_proto, "created_at"),
            updated_at=timestamp_from_protobuf(measurement_proto, "updated_at"),
            created_by=measurement_proto.created_by,
            updated_by=measurement_proto.updated_by,
        )

    def to_protobuf(self) -> MeasurementProto:
        """Convert this Measurement to a protobuf Measurement message.

        Output-only fields, such as value_type and conditions, are not included in
        protobuf requests.
        """
        return MeasurementProto(
            id=self.id,
            test_result_id=self.test_result_id,
            step_id=self.step_id,
            name=self.name,
            value=measurement_value_to_protobuf(self.value),
            upper_limit=measurement_value_to_protobuf(self.upper_limit),
            lower_limit=measurement_value_to_protobuf(self.lower_limit),
            units=self.units or (self.value.units if isinstance(self.value, Scalar) else ""),
            notes=self.notes,
            start_date_time=timestamp_to_protobuf(self.start_date_time),
            end_date_time=timestamp_to_protobuf(self.end_date_time),
            duration=duration_to_protobuf(self.duration),
            outcome=self.outcome.to_protobuf(),
            error_information=(
                self.error_information.to_protobuf() if self.error_information is not None else None
            ),
            extension=extension_to_protobuf(self.extension),
            schema_id=self.schema_id,
            software_item_ids=self.software_item_ids,
            hardware_item_ids=self.hardware_item_ids,
            test_adapter_ids=self.test_adapter_ids,
            software_items=[item.to_protobuf() for item in self.software_items],
            hardware_items=[item.to_protobuf() for item in self.hardware_items],
            test_adapters=[adapter.to_protobuf() for adapter in self.test_adapters],
            comparison_type=self.comparison_type,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Measurement):
            return NotImplemented
        return (
            self.id == other.id
            and self.test_result_id == other.test_result_id
            and self.step_id == other.step_id
            and self.name == other.name
            and _values_equal(self.value, other.value)
            and _values_equal(self.upper_limit, other.upper_limit)
            and _values_equal(self.lower_limit, other.lower_limit)
            and self.value_type == other.value_type
            and self.units == other.units
            and self.notes == other.notes
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.duration == other.duration
            and self.outcome == other.outcome
            and self.error_information == other.error_information
            and self.extension == other.extension
            and self.schema_id == other.schema_id
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.software_items == other.software_items
            and self.hardware_items == other.hardware_items
            and self.test_adapters == other.test_adapters
            and self.comparison_type == other.comparison_type
            and self.conditions == other.conditions
            and self.created_at == other.created_at
            and self.updated_at == other.updated_at
            and self.created_by == other.created_by
            and self.updated_by == other.updated_by
        )

    def __str__(self) -> str:
        """Return a string representation of the Measurement."""
        return str(self.to_protobuf())


def _values_equal(left: object, right: object) -> bool:
    # Waveform equality returns arrays, so compare through the protobuf form.
    if left is None or right is None:
        return left is right
    return measurement_value_to_protobuf(_as_scalar(left)) == measurement_value_to_protobuf(
        _as_scalar(right)
    )


def _as_scalar(value: object) -> object:
    # Normalize plain values so protobuf comparison includes Scalar unit attributes.
    return Scalar(value) if isinstance(value, (bool, int, float, str)) else value
