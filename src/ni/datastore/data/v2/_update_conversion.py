"""Conversion of update fields to V2 update requests."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast
from uuid import UUID

import hightime as ht
from google.protobuf import json_format
from google.protobuf.descriptor import Descriptor
from google.protobuf.field_mask_pb2 import FieldMask
from ni.measurements.data.v2.data_store_pb2 import (
    Measurement as MeasurementProto,
    Step as StepProto,
    TestResult as TestResultProto,
)
from ni.protobuf.types.precision_duration_conversion import hightime_timedelta_to_protobuf
from ni.protobuf.types.precision_timestamp_conversion import hightime_datetime_to_protobuf

from ni.datastore.data.v2._grpc_conversion import id_string, string_list
from ni.datastore.data.v2._types._error_information import ErrorInformation

# Mutable update-mask paths from the V2 mutability design, including Stage 2 resource fields.
TEST_RESULT_UPDATE_FIELDS = frozenset(
    {
        "uut_instance_id",
        "uut_id",
        "operator_id",
        "test_station_id",
        "test_description_id",
        "uut_instance",
        "uut",
        "operator",
        "test_station",
        "test_description",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "status",
        "error_information",
        "link",
        "keywords",
        "extension",
    }
)
STEP_UPDATE_FIELDS = frozenset(
    {
        "test_id",
        "test",
        "notes",
        "start_date_time",
        "end_date_time",
        "duration",
        "outcome",
        "status",
        "error_information",
        "link",
        "keywords",
        "extension",
    }
)
MEASUREMENT_UPDATE_FIELDS = frozenset(
    {
        "notes",
        "outcome",
        "error_information",
        "extension",
        "start_date_time",
        "end_date_time",
        "duration",
    }
)

# Stage 2 fields that the service does not accept in an update mask yet. A whole-resource
# update selects them only when they have a value, so it still works with the current service.
_STAGE_2_UPDATE_FIELDS = frozenset({"uut_id", "uut", "keywords", "duration"})

# Relationships that are set by ID or alias, or by inline metadata, but never both.
TEST_RESULT_RELATIONSHIPS = {
    "uut_instance_id": "uut_instance",
    "uut_id": "uut",
    "operator_id": "operator",
    "test_station_id": "test_station",
    "test_description_id": "test_description",
}
STEP_RELATIONSHIPS = {"test_id": "test"}

# Update fields that take a metadata model, such as Operator, and are sent as its protobuf.
_METADATA_UPDATE_FIELDS = frozenset(
    {"uut_instance", "uut", "operator", "test_station", "test_description", "test"}
)


def populate_update(
    resource: TestResultProto | StepProto | MeasurementProto,
    fields: Mapping[str, object],
    allowed: frozenset[str],
) -> FieldMask:
    """Copy update field values into a protobuf resource and return the update mask."""
    if not fields:
        raise ValueError("At least one field must be supplied for an update.")
    unknown_fields = fields.keys() - allowed
    if unknown_fields:
        raise ValueError(f"Fields cannot be updated: {', '.join(sorted(unknown_fields))}.")

    target = cast(Any, resource)
    for name, value in fields.items():
        if value is None:
            target.ClearField(name)
        elif name in {"start_date_time", "end_date_time"}:
            getattr(target, name).CopyFrom(hightime_datetime_to_protobuf(cast(ht.datetime, value)))
        elif name == "duration":
            target.duration.CopyFrom(hightime_timedelta_to_protobuf(cast(ht.timedelta, value)))
        elif name == "keywords":
            target.keywords[:] = string_list(cast(Iterable[str], value), "keywords")
        elif name == "extension":
            json_format.ParseDict(dict(cast(Mapping[str, Any], value)), target.extension)
        elif name == "error_information":
            target.error_information.CopyFrom(cast(ErrorInformation, value).to_protobuf())
        elif name in _METADATA_UPDATE_FIELDS:
            getattr(target, name).CopyFrom(cast(Any, value).to_protobuf())
        elif isinstance(value, UUID):
            setattr(target, name, id_string(value))
        else:
            setattr(target, name, value)

    return FieldMask(paths=list(fields))


def resource_update_fields(
    resource: object,
    descriptor: Descriptor,
    allowed: frozenset[str],
    relationships: Mapping[str, str],
) -> dict[str, object]:
    """Select every updatable field of a resource, in protobuf field order.

    Empty values are selected too, so the update clears them. Stage 2 fields are
    selected only when they have a value. When a relationship has both an ID and
    inline metadata, such as an expanded read, only the ID is sent.
    """
    fields: dict[str, object] = {}
    for field in descriptor.fields:
        if field.name not in allowed:
            continue
        value = getattr(resource, field.name)
        if field.name in _STAGE_2_UPDATE_FIELDS and not value:
            continue
        if field.name == "extension" and not value:
            value = None
        fields[field.name] = value

    for id_field, inline_field in relationships.items():
        if fields.get(id_field) and fields.get(inline_field) is not None:
            fields[inline_field] = None
    return fields
