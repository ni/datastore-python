"""Datastore client for publishing and reading data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Generic, Type, TypeVar

from google.protobuf import any_pb2

from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)

from ni.datastore.publish_converters import (
    BoolPublishConverter,
    AnalogWaveformPublishConverter,
    ComplexWaveformPublishConverter,
    DigitalWaveformPublishConverter,
    IntPublishConverter,
    FloatPublishConverter,
    ScalarPublishConverter,
    VectorPublishConverter,
    VectorPublishBatchConverter,
    SpectrumPublishConverter,
    PublishConverter,
    PublishBatchConverter,
)

from ni.datastore.read_converters import (
    DoubleAnalogWaveformReadConverter,
    DoubleComplexWaveformReadConverter,
    DoubleSpectrumReadConverter,
    DigitalWaveformReadConverter,
    I16AnalogWaveformReadConverter,
    I16ComplexWaveformReadConverter,
    ReadConverter,
    VectorReadConverter,
)

_PUBLISH_CONVERTERS: list[PublishConverter] = [
    BoolPublishConverter(),
    AnalogWaveformPublishConverter(),
    ComplexWaveformPublishConverter(),
    DigitalWaveformPublishConverter(),
    IntPublishConverter(),
    FloatPublishConverter(),
    ScalarPublishConverter(),
    VectorPublishConverter(),
    SpectrumPublishConverter(),
]

_PUBLISH_BATCH_CONVERTERS: list[PublishBatchConverter] = [
    VectorPublishBatchConverter(),
]

_READ_CONVERTERS: list[ReadConverter] = [
    DoubleAnalogWaveformReadConverter(),
    DoubleComplexWaveformReadConverter(),
    DoubleSpectrumReadConverter(),
    DigitalWaveformReadConverter(),
    I16AnalogWaveformReadConverter(),
    I16ComplexWaveformReadConverter(),
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
    # TODO: Inspect python type and choose correct converter.
    converter = _PUBLISH_CONVERTERS_BY_PYTHON_TYPE["Dummy"]
    converter.populate_publish_condition_request_value(publish_request, value)


def populate_publish_condition_batch_request_values(
    publish_request: PublishConditionBatchRequest,
    values: object,
) -> None:
    """Populate publish condition batch request value."""
    # TODO: Inspect python type and choose correct converter.
    converter = _PUBLISH_BATCH_CONVERTERS_BY_PYTHON_TYPE["Dummy"]
    converter.populate_publish_condition_batch_request_values(publish_request, values)


def populate_publish_measurement_request_value(
    publish_request: PublishMeasurementRequest,
    value: object,
) -> None:
    """Populate publish measurement request value."""
    # TODO: Inspect python type and choose correct converter.
    converter = _PUBLISH_CONVERTERS_BY_PYTHON_TYPE["Dummy"]
    converter.populate_publish_measurement_request_value(publish_request, value)


def populate_publish_measurement_batch_request_values(
    publish_request: PublishMeasurementBatchRequest,
    values: object,
) -> None:
    """Populate publish measurement batch request values."""
    # TODO: Inspect python type and choose correct converter.
    converter = _PUBLISH_BATCH_CONVERTERS_BY_PYTHON_TYPE["Dummy"]
    converter.populate_publish_measurement_batch_request_values(publish_request, values)
