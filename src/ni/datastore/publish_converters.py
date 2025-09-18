"""Datastore client for publishing and reading data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Generic, Type, TypeVar

from google.protobuf import any_pb2
from google.protobuf.message import Message

import numpy as np
from google.protobuf.any_pb2 import Any

from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)

from ni.protobuf.types.scalar_conversion import scalar_to_protobuf
from ni.protobuf.types.vector_conversion import vector_to_protobuf
from ni.protobuf.types.vector_pb2 import Vector as VectorProto
from ni.protobuf.types.waveform_conversion import (
    digital_waveform_to_protobuf,
    float64_analog_waveform_to_protobuf,
    float64_complex_waveform_to_protobuf,
    float64_spectrum_to_protobuf,
    int16_analog_waveform_to_protobuf,
    int16_complex_waveform_to_protobuf,
)
from ni.protobuf.types.xydata_pb2 import DoubleXYData
from nitypes.bintime import DateTime
from nitypes.complex import ComplexInt32Base
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum

_TPythonType = TypeVar("_TPythonType")


class PublishConverter(Generic[_TPythonType], ABC):
    """A class that defines how to convert between Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def python_type(self) -> type:
        """The Python type that this converter handles."""

    @property
    def python_typename(self) -> str:
        """The Python type name that this converter handles."""
        return f"{self.python_type.__module__}.{self.python_type.__name__}"

    @abstractmethod
    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: _TPythonType,
    ) -> None:
        """Populate publish condition request value."""

    @abstractmethod
    def populate_publish_condition_batch_request_values(
        self,
        publish_request: PublishConditionBatchRequest,
        values: _TPythonType,
    ) -> None:
        """Populate publish condition batch request value."""

    @abstractmethod
    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: _TPythonType,
    ) -> None:
        """Populate publish measurement request value."""

    @abstractmethod
    def populate_publish_measurement_batch_request_values(
        self,
        publish_request: PublishMeasurementBatchRequest,
        values: _TPythonType,
    ) -> None:
        """Populate publish measurement batch request values."""


class BoolConverter(PublishConverter[bool]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return bool

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: bool,
    ) -> None:
        """Populate publish condition request value."""
        publish_request.scalar.bool_value = value

    def populate_publish_condition_batch_request_values(
        self,
        publish_request: PublishConditionBatchRequest,
        values: bool,
    ) -> None:
        """Populate publish condition batch request value."""
        raise NotImplementedError("Unsupported condition values type: bool")

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: bool,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.scalar.bool_value = value

    def populate_publish_measurement_batch_request_values(
        self,
        publish_request: PublishMeasurementBatchRequest,
        values: bool,
    ) -> None:
        """Populate publish measurement batch request values."""


# TODO: We may wish to separate out some of the conversion code below.
def populate_publish_condition_request_value(
    publish_request: PublishConditionRequest, value: object
) -> None:
    # TODO: Determine whether we wish to support primitive types such as float
    # TODO: or require wrapping in a Scalar.
    if isinstance(value, bool):
        publish_request.scalar.bool_value = value
    elif isinstance(value, int):
        publish_request.scalar.sint32_value = value
    elif isinstance(value, float):
        publish_request.scalar.double_value = value
    elif isinstance(value, str):
        publish_request.scalar.string_value = value
    elif isinstance(value, Scalar):
        publish_request.scalar.CopyFrom(scalar_to_protobuf(value))
    else:
        raise TypeError(
            f"Unsupported condition value type: {type(value)}. Please consult the docummentation."
        )

def populate_publish_condition_batch_request_values(
    publish_request: PublishConditionBatchRequest, values: object
) -> None:
    # TODO: Determine whether we wish to support primitive types such as a list of float
    if isinstance(values, Vector):
        publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
    else:
        raise TypeError(
            f"Unsupported condition values type: {type(values)}. Please consult the docummentation."
        )

def populate_publish_measurement_request_value(
    publish_request: PublishMeasurementRequest, value: object
) -> None:
    # TODO: Determine whether we wish to support primitive types such as float
    # TODO: or require wrapping in a Scalar.
    if isinstance(value, bool):
        publish_request.scalar.bool_value = value
    elif isinstance(value, int):
        publish_request.scalar.sint32_value = value
    elif isinstance(value, float):
        publish_request.scalar.double_value = value
    elif isinstance(value, str):
        publish_request.scalar.string_value = value
    elif isinstance(value, Scalar):
        publish_request.scalar.CopyFrom(scalar_to_protobuf(value))
    elif isinstance(value, Vector):
        publish_request.vector.CopyFrom(vector_to_protobuf(value))
    elif isinstance(value, AnalogWaveform):
        if value.dtype == np.float64:
            publish_request.double_analog_waveform.CopyFrom(
                float64_analog_waveform_to_protobuf(value)
            )
        elif value.dtype == np.int16:
            publish_request.i16_analog_waveform.CopyFrom(
                int16_analog_waveform_to_protobuf(value)
            )
        else:
            raise TypeError(f"Unsupported AnalogWaveform dtype: {value.dtype}")
    elif isinstance(value, ComplexWaveform):
        if value.dtype == np.complex128:
            publish_request.double_complex_waveform.CopyFrom(
                float64_complex_waveform_to_protobuf(value)
            )
        elif value.dtype == ComplexInt32Base:
            publish_request.i16_complex_waveform.CopyFrom(
                int16_complex_waveform_to_protobuf(value)
            )
        else:
            raise TypeError(f"Unsupported ComplexWaveform dtype: {value.dtype}")
    elif isinstance(value, Spectrum):
        if value.dtype == np.float64:
            publish_request.double_spectrum.CopyFrom(float64_spectrum_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported Spectrum dtype: {value.dtype}")
    elif isinstance(value, DigitalWaveform):
        publish_request.digital_waveform.CopyFrom(digital_waveform_to_protobuf(value))
    else:
        raise TypeError(
            f"Unsupported measurement value type: {type(value)}. Please consult the docummentation."
        )
    # TODO: Implement conversion from proper XYData type

def populate_publish_measurement_batch_request_values(
    publish_request: PublishMeasurementBatchRequest, values: object
) -> None:
    # TODO: Determine whether we wish to support primitive types such as a list of float
    if isinstance(values, Vector):
        publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
    else:
        raise TypeError(
            f"Unsupported measurement values type: {type(values)}. Please consult the docummentation."
        )
