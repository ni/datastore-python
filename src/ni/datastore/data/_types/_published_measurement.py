"""Published Measurement data type for the Data Store Client."""

from __future__ import annotations

from typing import Iterable, MutableSequence

import hightime as ht
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.datastore.data._types._published_condition import PublishedCondition
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedMeasurement as PublishedMeasurementProto,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_from_protobuf,
    hightime_datetime_to_protobuf,
)


class PublishedMeasurement:
    """Information about a measurement published to the data store."""

    __slots__ = (
        "moniker",
        "_published_conditions",
        "_id",
        "test_result_id",
        "step_id",
        "_software_item_ids",
        "_hardware_item_ids",
        "_test_adapter_ids",
        "measurement_name",
        "data_type",
        "measurement_notes",
        "start_date_time",
        "end_date_time",
        "outcome",
        "parametric_index",
        "error_information",
    )

    @property
    def published_conditions(self) -> MutableSequence[PublishedCondition]:
        """The published conditions associated with the published measurement."""
        return self._published_conditions

    @property
    def software_item_ids(self) -> MutableSequence[str]:
        """The software item IDs associated with the published measurement."""
        return self._software_item_ids

    @property
    def hardware_item_ids(self) -> MutableSequence[str]:
        """The hardware item IDs associated with the published measurement."""
        return self._hardware_item_ids

    @property
    def test_adapter_ids(self) -> MutableSequence[str]:
        """The test adapter IDs associated with the published measurement."""
        return self._test_adapter_ids

    @property
    def id(self) -> str:
        """The id string associated with the published measurement."""
        return self._id

    def __init__(
        self,
        *,
        moniker: Moniker | None = None,
        published_conditions: Iterable[PublishedCondition] | None = None,
        id: str = "",
        test_result_id: str = "",
        step_id: str = "",
        software_item_ids: Iterable[str] | None = None,
        hardware_item_ids: Iterable[str] | None = None,
        test_adapter_ids: Iterable[str] | None = None,
        measurement_name: str = "",
        data_type: str = "",
        measurement_notes: str = "",
        start_date_time: ht.datetime | None = None,
        end_date_time: ht.datetime | None = None,
        outcome: Outcome.ValueType = Outcome.OUTCOME_UNSPECIFIED,
        parametric_index: int = 0,
        error_information: ErrorInformation | None = None,
    ) -> None:
        """Initialize a PublishedMeasurement instance."""
        self.moniker = moniker
        self._published_conditions: MutableSequence[PublishedCondition] = (
            list(published_conditions) if published_conditions is not None else []
        )
        self._id = id
        self.test_result_id = test_result_id
        self.step_id = step_id
        self._software_item_ids: MutableSequence[str] = (
            list(software_item_ids) if software_item_ids is not None else []
        )
        self._hardware_item_ids: MutableSequence[str] = (
            list(hardware_item_ids) if hardware_item_ids is not None else []
        )
        self._test_adapter_ids: MutableSequence[str] = (
            list(test_adapter_ids) if test_adapter_ids is not None else []
        )
        self.measurement_name = measurement_name
        self.data_type = data_type
        self.measurement_notes = measurement_notes
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.outcome = outcome
        self.parametric_index = parametric_index
        self.error_information = error_information

    @staticmethod
    def from_protobuf(
        published_measurement_proto: PublishedMeasurementProto,
    ) -> "PublishedMeasurement":
        """Create a PublishedMeasurement instance from a protobuf PublishedMeasurement message."""
        return PublishedMeasurement(
            moniker=(
                published_measurement_proto.moniker
                if published_measurement_proto.HasField("moniker")
                else None
            ),
            published_conditions=[
                PublishedCondition.from_protobuf(cond)
                for cond in published_measurement_proto.published_conditions
            ],
            id=published_measurement_proto.id,
            test_result_id=published_measurement_proto.test_result_id,
            step_id=published_measurement_proto.step_id,
            software_item_ids=published_measurement_proto.software_item_ids,
            hardware_item_ids=published_measurement_proto.hardware_item_ids,
            test_adapter_ids=published_measurement_proto.test_adapter_ids,
            measurement_name=published_measurement_proto.measurement_name,
            data_type=published_measurement_proto.data_type,
            measurement_notes=published_measurement_proto.measurement_notes,
            start_date_time=(
                hightime_datetime_from_protobuf(published_measurement_proto.start_date_time)
                if published_measurement_proto.HasField("start_date_time")
                else None
            ),
            end_date_time=(
                hightime_datetime_from_protobuf(published_measurement_proto.end_date_time)
                if published_measurement_proto.HasField("end_date_time")
                else None
            ),
            outcome=published_measurement_proto.outcome,
            parametric_index=published_measurement_proto.parametric_index,
            error_information=(
                published_measurement_proto.error_information
                if published_measurement_proto.HasField("error_information")
                else None
            ),
        )

    def to_protobuf(self) -> PublishedMeasurementProto:
        """Convert this PublishedMeasurement instance to a protobuf PublishedMeasurement message."""
        return PublishedMeasurementProto(
            moniker=self.moniker,
            published_conditions=[
                condition.to_protobuf() for condition in self.published_conditions
            ],
            id=self.id,
            test_result_id=self.test_result_id,
            step_id=self.step_id,
            software_item_ids=self.software_item_ids,
            hardware_item_ids=self.hardware_item_ids,
            test_adapter_ids=self.test_adapter_ids,
            measurement_name=self.measurement_name,
            data_type=self.data_type,
            measurement_notes=self.measurement_notes,
            start_date_time=(
                hightime_datetime_to_protobuf(self.start_date_time)
                if self.start_date_time is not None
                else None
            ),
            end_date_time=(
                hightime_datetime_to_protobuf(self.end_date_time)
                if self.end_date_time is not None
                else None
            ),
            outcome=self.outcome,
            parametric_index=self.parametric_index,
            error_information=self.error_information,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, PublishedMeasurement):
            return NotImplemented
        return (
            self.moniker == other.moniker
            and self.published_conditions == other.published_conditions
            and self.id == other.id
            and self.test_result_id == other.test_result_id
            and self.step_id == other.step_id
            and self.software_item_ids == other.software_item_ids
            and self.hardware_item_ids == other.hardware_item_ids
            and self.test_adapter_ids == other.test_adapter_ids
            and self.measurement_name == other.measurement_name
            and self.data_type == other.data_type
            and self.measurement_notes == other.measurement_notes
            and self.start_date_time == other.start_date_time
            and self.end_date_time == other.end_date_time
            and self.outcome == other.outcome
            and self.parametric_index == other.parametric_index
            and self.error_information == other.error_information
        )

    def __str__(self) -> str:
        """Return a string representation of the PublishedMeasurement."""
        return str(self.to_protobuf())
