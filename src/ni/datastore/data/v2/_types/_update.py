"""Update builders and typed update fields for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypedDict
from uuid import UUID

import hightime as ht
from google.protobuf.field_mask_pb2 import FieldMask
from ni.measurements.data.v2.data_store_pb2 import (
    Measurement as MeasurementProto,
    Step as StepProto,
    TestResult as TestResultProto,
)
from ni.measurements.data.v2.data_store_service_pb2 import (
    UpdateMeasurementRequest,
    UpdateStepRequest,
    UpdateTestResultRequest,
)

from ni.datastore.data.v2._grpc_conversion import id_string, string_list
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._status import Status
from ni.datastore.data.v2._types._step import Step
from ni.datastore.data.v2._types._test_result import TestResult
from ni.datastore.data.v2._update_conversion import (
    MEASUREMENT_UPDATE_FIELDS,
    populate_update,
    STEP_UPDATE_FIELDS,
    TEST_RESULT_UPDATE_FIELDS,
)
from ni.datastore.metadata import (
    Operator,
    Test,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)


class TestResultUpdateFields(TypedDict, total=False):
    """The test result fields that update_test_result accepts as keyword arguments.

    A value of None clears the field. uut_id, uut, keywords, and duration are
    Stage 2 fields that the service may not support yet.
    """

    uut_instance_id: str | UUID | None
    uut_id: str | UUID | None
    operator_id: str | UUID | None
    test_station_id: str | UUID | None
    test_description_id: str | UUID | None
    uut_instance: UutInstance | None
    uut: Uut | None
    operator: Operator | None
    test_station: TestStation | None
    test_description: TestDescription | None
    start_date_time: ht.datetime | None
    end_date_time: ht.datetime | None
    duration: ht.timedelta | None
    outcome: Outcome | None
    status: Status | None
    error_information: ErrorInformation | None
    link: str | None
    keywords: Iterable[str] | None
    extension: Mapping[str, Any] | None


class StepUpdateFields(TypedDict, total=False):
    """The step fields that update_step accepts as keyword arguments.

    A value of None clears the field. keywords and duration are Stage 2 fields
    that the service may not support yet.
    """

    test_id: str | UUID | None
    test: Test | None
    notes: str | None
    start_date_time: ht.datetime | None
    end_date_time: ht.datetime | None
    duration: ht.timedelta | None
    outcome: Outcome | None
    status: Status | None
    error_information: ErrorInformation | None
    link: str | None
    keywords: Iterable[str] | None
    extension: Mapping[str, Any] | None


class MeasurementUpdateFields(TypedDict, total=False):
    """The measurement fields that update_measurement accepts as keyword arguments.

    A value of None clears the field. duration is a Stage 2 field that the
    service may not support yet.
    """

    notes: str | None
    start_date_time: ht.datetime | None
    end_date_time: ht.datetime | None
    duration: ht.timedelta | None
    outcome: Outcome | None
    error_information: ErrorInformation | None
    extension: Mapping[str, Any] | None


class TestResultUpdateBuilder:
    """Builds an update for an existing test result.

    Each with method sets a field and adds it to the update mask. Only the
    selected fields change. None clears a selected field. For a relationship
    that can be set by ID or by inline metadata, such as operator_id and
    operator, the last call wins and the other form is not sent. Values are
    copied when each with method is called.

    Example:
        update = TestResultUpdateBuilder(test_result).with_outcome(Outcome.PASSED)
        updated = data_store_client.update_test_result(update)
    """

    __slots__ = ("_test_result", "_paths")

    def __init__(self, test_result: TestResult | str | UUID) -> None:
        """Start an update for a test result without selecting any fields.

        Args:
            test_result: The test result to update, or its ID.

        Raises:
            ValueError: If the ID is empty.
        """
        self._test_result = TestResultProto(id=_target_id(test_result, "test result"))
        self._paths: dict[str, None] = {}

    def with_start_date_time(self, start_date_time: ht.datetime | None) -> TestResultUpdateBuilder:
        """Set the start date and time, or clear it with None."""
        return self._select("start_date_time", start_date_time)

    def with_end_date_time(self, end_date_time: ht.datetime | None) -> TestResultUpdateBuilder:
        """Set the end date and time, or clear it with None."""
        return self._select("end_date_time", end_date_time)

    def with_duration(self, duration: ht.timedelta | None) -> TestResultUpdateBuilder:
        """Set the duration, or clear it with None. The service may not support this yet."""
        return self._select("duration", duration)

    def with_status(self, status: Status) -> TestResultUpdateBuilder:
        """Set the lifecycle status."""
        return self._select("status", status)

    def with_outcome(self, outcome: Outcome) -> TestResultUpdateBuilder:
        """Set the outcome."""
        return self._select("outcome", outcome)

    def with_error_information(
        self, error_information: ErrorInformation | None
    ) -> TestResultUpdateBuilder:
        """Set the error information, or clear it with None."""
        return self._select("error_information", error_information)

    def with_extension(self, extension: Mapping[str, Any] | None) -> TestResultUpdateBuilder:
        """Replace the whole extension JSON document, or clear it with None."""
        return self._select("extension", None if extension is None else dict(extension))

    def with_link(self, link: str | None) -> TestResultUpdateBuilder:
        """Set the link, or clear it with None."""
        return self._select("link", link)

    def with_keywords(self, keywords: Iterable[str] | None) -> TestResultUpdateBuilder:
        """Replace the keywords, or clear them with None. The service may not support this yet."""
        return self._select(
            "keywords", None if keywords is None else string_list(keywords, "keywords")
        )

    def with_uut_instance_id(self, uut_instance_id: str | UUID | None) -> TestResultUpdateBuilder:
        """Link a UUT instance by ID or alias, or unlink it with None."""
        return self._select("uut_instance_id", uut_instance_id, "uut_instance")

    def with_uut_instance(self, uut_instance: UutInstance | None) -> TestResultUpdateBuilder:
        """Link a UUT instance found or created from inline metadata, or unlink it with None."""
        return self._select("uut_instance", uut_instance, "uut_instance_id")

    def with_uut_id(self, uut_id: str | UUID | None) -> TestResultUpdateBuilder:
        """Link a UUT by ID or alias, or unlink it with None.

        The service may not support this yet.
        """
        return self._select("uut_id", uut_id, "uut")

    def with_uut(self, uut: Uut | None) -> TestResultUpdateBuilder:
        """Link a UUT from inline metadata, or unlink it with None.

        The service may not support this yet.
        """
        return self._select("uut", uut, "uut_id")

    def with_operator_id(self, operator_id: str | UUID | None) -> TestResultUpdateBuilder:
        """Link an operator by ID or alias, or unlink it with None."""
        return self._select("operator_id", operator_id, "operator")

    def with_operator(self, operator: Operator | None) -> TestResultUpdateBuilder:
        """Link an operator found or created from inline metadata, or unlink it with None."""
        return self._select("operator", operator, "operator_id")

    def with_test_station_id(self, test_station_id: str | UUID | None) -> TestResultUpdateBuilder:
        """Link a test station by ID or alias, or unlink it with None."""
        return self._select("test_station_id", test_station_id, "test_station")

    def with_test_station(self, test_station: TestStation | None) -> TestResultUpdateBuilder:
        """Link a test station found or created from inline metadata, or unlink it with None."""
        return self._select("test_station", test_station, "test_station_id")

    def with_test_description_id(
        self, test_description_id: str | UUID | None
    ) -> TestResultUpdateBuilder:
        """Link a test description by ID or alias, or unlink it with None."""
        return self._select("test_description_id", test_description_id, "test_description")

    def with_test_description(
        self, test_description: TestDescription | None
    ) -> TestResultUpdateBuilder:
        """Link a test description found or created from inline metadata, or unlink it with None."""
        return self._select("test_description", test_description, "test_description_id")

    def build_update(self) -> UpdateTestResultRequest:
        """Build the update request.

        Raises:
            ValueError: If no fields are selected.
        """
        return UpdateTestResultRequest(
            test_result=self._test_result, update_mask=_update_mask(self._paths)
        )

    def _select(self, name: str, value: object, other: str = "") -> TestResultUpdateBuilder:
        _select(self._test_result, self._paths, TEST_RESULT_UPDATE_FIELDS, name, value, other)
        return self


class StepUpdateBuilder:
    """Builds an update for an existing step.

    Each with method sets a field and adds it to the update mask. Only the
    selected fields change. None clears a selected field. For the test, set by
    test_id or by inline metadata, the last call wins and the other form is not
    sent. Values are copied when each with method is called.

    Example:
        update = StepUpdateBuilder(step).with_outcome(Outcome.PASSED).with_notes("Verified")
        updated = data_store_client.update_step(update)
    """

    __slots__ = ("_step", "_paths")

    def __init__(self, step: Step | str | UUID) -> None:
        """Start an update for a step without selecting any fields.

        Args:
            step: The step to update, or its ID.

        Raises:
            ValueError: If the ID is empty.
        """
        self._step = StepProto(id=_target_id(step, "step"))
        self._paths: dict[str, None] = {}

    def with_start_date_time(self, start_date_time: ht.datetime | None) -> StepUpdateBuilder:
        """Set the start date and time, or clear it with None."""
        return self._select("start_date_time", start_date_time)

    def with_end_date_time(self, end_date_time: ht.datetime | None) -> StepUpdateBuilder:
        """Set the end date and time, or clear it with None."""
        return self._select("end_date_time", end_date_time)

    def with_duration(self, duration: ht.timedelta | None) -> StepUpdateBuilder:
        """Set the duration, or clear it with None. The service may not support this yet."""
        return self._select("duration", duration)

    def with_status(self, status: Status) -> StepUpdateBuilder:
        """Set the lifecycle status."""
        return self._select("status", status)

    def with_outcome(self, outcome: Outcome) -> StepUpdateBuilder:
        """Set the outcome."""
        return self._select("outcome", outcome)

    def with_error_information(
        self, error_information: ErrorInformation | None
    ) -> StepUpdateBuilder:
        """Set the error information, or clear it with None."""
        return self._select("error_information", error_information)

    def with_extension(self, extension: Mapping[str, Any] | None) -> StepUpdateBuilder:
        """Replace the whole extension JSON document, or clear it with None."""
        return self._select("extension", None if extension is None else dict(extension))

    def with_notes(self, notes: str | None) -> StepUpdateBuilder:
        """Set the notes, or clear them with None."""
        return self._select("notes", notes)

    def with_link(self, link: str | None) -> StepUpdateBuilder:
        """Set the link, or clear it with None."""
        return self._select("link", link)

    def with_keywords(self, keywords: Iterable[str] | None) -> StepUpdateBuilder:
        """Replace the keywords, or clear them with None. The service may not support this yet."""
        return self._select(
            "keywords", None if keywords is None else string_list(keywords, "keywords")
        )

    def with_test_id(self, test_id: str | UUID | None) -> StepUpdateBuilder:
        """Link a test by ID or alias, or unlink it with None."""
        return self._select("test_id", test_id, "test")

    def with_test(self, test: Test | None) -> StepUpdateBuilder:
        """Link a test found or created from inline metadata, or unlink it with None."""
        return self._select("test", test, "test_id")

    def build_update(self) -> UpdateStepRequest:
        """Build the update request.

        Raises:
            ValueError: If no fields are selected.
        """
        return UpdateStepRequest(step=self._step, update_mask=_update_mask(self._paths))

    def _select(self, name: str, value: object, other: str = "") -> StepUpdateBuilder:
        _select(self._step, self._paths, STEP_UPDATE_FIELDS, name, value, other)
        return self


class MeasurementUpdateBuilder:
    """Builds an update for an existing measurement.

    Each with method sets a field and adds it to the update mask. Only the
    selected fields change. None clears a selected field. Values are copied when
    each with method is called. The value, units, and limits cannot be updated.

    Example:
        update = MeasurementUpdateBuilder(measurement).with_notes("Rechecked")
        updated = data_store_client.update_measurement(update)
    """

    __slots__ = ("_measurement", "_paths")

    def __init__(self, measurement: Measurement | str | UUID) -> None:
        """Start an update for a measurement without selecting any fields.

        Args:
            measurement: The measurement to update, or its ID.

        Raises:
            ValueError: If the ID is empty.
        """
        self._measurement = MeasurementProto(id=_target_id(measurement, "measurement"))
        self._paths: dict[str, None] = {}

    def with_start_date_time(self, start_date_time: ht.datetime | None) -> MeasurementUpdateBuilder:
        """Set the start date and time, or clear it with None."""
        return self._select("start_date_time", start_date_time)

    def with_end_date_time(self, end_date_time: ht.datetime | None) -> MeasurementUpdateBuilder:
        """Set the end date and time, or clear it with None."""
        return self._select("end_date_time", end_date_time)

    def with_duration(self, duration: ht.timedelta | None) -> MeasurementUpdateBuilder:
        """Set the duration, or clear it with None. The service may not support this yet."""
        return self._select("duration", duration)

    def with_outcome(self, outcome: Outcome) -> MeasurementUpdateBuilder:
        """Set the outcome."""
        return self._select("outcome", outcome)

    def with_error_information(
        self, error_information: ErrorInformation | None
    ) -> MeasurementUpdateBuilder:
        """Set the error information, or clear it with None."""
        return self._select("error_information", error_information)

    def with_extension(self, extension: Mapping[str, Any] | None) -> MeasurementUpdateBuilder:
        """Replace the whole extension JSON document, or clear it with None."""
        return self._select("extension", None if extension is None else dict(extension))

    def with_notes(self, notes: str | None) -> MeasurementUpdateBuilder:
        """Set the notes, or clear them with None."""
        return self._select("notes", notes)

    def build_update(self) -> UpdateMeasurementRequest:
        """Build the update request.

        Raises:
            ValueError: If no fields are selected.
        """
        return UpdateMeasurementRequest(
            measurement=self._measurement, update_mask=_update_mask(self._paths)
        )

    def _select(self, name: str, value: object) -> MeasurementUpdateBuilder:
        _select(self._measurement, self._paths, MEASUREMENT_UPDATE_FIELDS, name, value, "")
        return self


def _target_id(target: TestResult | Step | Measurement | str | UUID, resource_name: str) -> str:
    resource_id = id_string(target) if isinstance(target, (str, UUID)) else target.id
    if not resource_id.strip():
        raise ValueError(f"The {resource_name} ID must not be empty.")
    return resource_id


def _select(
    resource: TestResultProto | StepProto | MeasurementProto,
    paths: dict[str, None],
    allowed: frozenset[str],
    name: str,
    value: object,
    other: str,
) -> None:
    if other:
        resource.ClearField(other)  # type: ignore[arg-type]
        paths.pop(other, None)
    populate_update(resource, {name: value}, allowed)
    paths[name] = None


def _update_mask(paths: Mapping[str, None]) -> FieldMask:
    if not paths:
        raise ValueError("At least one field must be selected before building an update.")
    return FieldMask(paths=list(paths))
