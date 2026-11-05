"""Typed create fields for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypedDict
from uuid import UUID

import hightime as ht

from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._status import Status
from ni.datastore.data.v2._types._step import Step
from ni.datastore.metadata import (
    HardwareItem,
    Operator,
    SoftwareItem,
    Test,
    TestAdapter,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)


class TestResultCreateFields(TypedDict, total=False):
    """The test result fields that create_test_result accepts as keyword arguments.

    Each field has the same meaning and default as the matching TestResult
    constructor argument.
    """

    uut_instance_id: str | UUID
    uut_id: str | UUID
    operator_id: str | UUID
    test_station_id: str | UUID
    test_description_id: str | UUID
    uut_instance: UutInstance | None
    uut: Uut | None
    operator: Operator | None
    test_station: TestStation | None
    test_description: TestDescription | None
    software_item_ids: Iterable[str | UUID] | None
    hardware_item_ids: Iterable[str | UUID] | None
    test_adapter_ids: Iterable[str | UUID] | None
    software_items: Iterable[SoftwareItem] | None
    hardware_items: Iterable[HardwareItem] | None
    test_adapters: Iterable[TestAdapter] | None
    start_date_time: ht.datetime | None
    end_date_time: ht.datetime | None
    duration: ht.timedelta | None
    outcome: Outcome
    status: Status
    link: str
    keywords: Iterable[str] | None
    extension: Mapping[str, Any] | None
    schema_id: str
    error_information: ErrorInformation | None
    steps: Iterable[Step] | None


class StepCreateFields(TypedDict, total=False):
    """The step fields that create_step accepts as keyword arguments.

    Each field has the same meaning and default as the matching Step
    constructor argument.
    """

    parent_step_id: str | UUID
    test_result_id: str | UUID
    test_id: str | UUID
    test: Test | None
    step_type: str
    notes: str
    start_date_time: ht.datetime | None
    end_date_time: ht.datetime | None
    duration: ht.timedelta | None
    outcome: Outcome
    status: Status
    link: str
    keywords: Iterable[str] | None
    extension: Mapping[str, Any] | None
    schema_id: str
    error_information: ErrorInformation | None
    conditions: Iterable[Condition] | None
    measurements: Iterable[Measurement] | None
    children: Iterable[Step] | None
