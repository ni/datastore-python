"""Datastore client for publishing and reading data."""

from __future__ import annotations

from typing import Any

from google.protobuf import any_pb2
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)

from ni.datastore.publish_converters import (
    AnalogWaveformPublishConverter,
    BoolPublishConverter,
    ComplexWaveformPublishConverter,
    DigitalWaveformPublishConverter,
    FloatPublishConverter,
    IntPublishConverter,
    PublishBatchConverter,
    PublishConverter,
    ScalarPublishConverter,
    SpectrumPublishConverter,
    StringPublishConverter,
    VectorPublishConverter,
    VectorPublishBatchConverter,
)
from ni.datastore.read_converters import (
    DigitalWaveformReadConverter,
    DoubleAnalogWaveformReadConverter,
    DoubleComplexWaveformReadConverter,
    DoubleSpectrumReadConverter,
    I16AnalogWaveformReadConverter,
    I16ComplexWaveformReadConverter,
    ReadConverter,
    ScalarReadConverter,
    VectorReadConverter,
)

_PUBLISH_CONVERTERS: list[PublishConverter[Any]] = [
    BoolPublishConverter(),
    AnalogWaveformPublishConverter(),
    ComplexWaveformPublishConverter(),
    DigitalWaveformPublishConverter(),
    IntPublishConverter(),
    FloatPublishConverter(),
    StringPublishConverter(),
    ScalarPublishConverter(),
    VectorPublishConverter(),
    SpectrumPublishConverter(),
]

_PUBLISH_BATCH_CONVERTERS: list[PublishBatchConverter[Any]] = [
    VectorPublishBatchConverter(),
]

_READ_CONVERTERS: list[ReadConverter[Any]] = [
    DoubleAnalogWaveformReadConverter(),
    DoubleComplexWaveformReadConverter(),
    DoubleSpectrumReadConverter(),
    DigitalWaveformReadConverter(),
    I16AnalogWaveformReadConverter(),
    I16ComplexWaveformReadConverter(),
    ScalarReadConverter(),
    VectorReadConverter(),
]

_READ_CONVERTERS_BY_PROTOBUF_TYPE = {entry.protobuf_typename: entry for entry in _READ_CONVERTERS}
_PUBLISH_CONVERTERS_BY_PYTHON_TYPE = {entry.python_typename: entry for entry in _PUBLISH_CONVERTERS}
_PUBLISH_BATCH_CONVERTERS_BY_PYTHON_TYPE = {entry.python_typename: entry for entry in _PUBLISH_BATCH_CONVERTERS}


def convert_from_protobuf(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()

    converter = _READ_CONVERTERS_BY_PROTOBUF_TYPE[underlying_typename]
    return converter.to_python(protobuf_any)


def populate_publish_condition_request_value(
    publish_request: PublishConditionRequest,
    value: object,
) -> None:
    """Populate publish condition request value."""
    converter = _get_publish_converter(value)
    converter.populate_publish_condition_request_value(publish_request, value)


def populate_publish_condition_batch_request_values(
    publish_request: PublishConditionBatchRequest,
    values: object,
) -> None:
    """Populate publish condition batch request value."""
    converter = _get_publish_batch_converter(values)
    converter.populate_publish_condition_batch_request_values(publish_request, values)


def populate_publish_measurement_request_value(
    publish_request: PublishMeasurementRequest,
    value: object,
) -> None:
    """Populate publish measurement request value."""
    converter = _get_publish_converter(value)
    converter.populate_publish_measurement_request_value(publish_request, value)


def populate_publish_measurement_batch_request_values(
    publish_request: PublishMeasurementBatchRequest,
    values: object,
) -> None:
    """Populate publish measurement batch request values."""
    converter = _get_publish_batch_converter(values)
    converter.populate_publish_measurement_batch_request_values(publish_request, values)


def _get_publish_converter(python_value: object) -> PublishConverter[Any]:
    type_string = _get_type_string(python_value)
    if type_string not in _PUBLISH_CONVERTERS_BY_PYTHON_TYPE.keys():
        raise TypeError(f"Invalid publish converter type string: {type_string}")
    return _PUBLISH_CONVERTERS_BY_PYTHON_TYPE[type_string]


def _get_publish_batch_converter(python_value: object) -> PublishBatchConverter[Any]:
    type_string = _get_type_string(python_value)
    if type_string not in _PUBLISH_BATCH_CONVERTERS_BY_PYTHON_TYPE.keys():
        raise TypeError(f"Invalid publish converter type string: {type_string}")
    return _PUBLISH_BATCH_CONVERTERS_BY_PYTHON_TYPE[type_string]


def _get_type_string(python_value: object) -> str:
    value_type = type(python_value)
    return f"{value_type.__module__}.{value_type.__name__}"
