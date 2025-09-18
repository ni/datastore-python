"""Datastore client for publishing and reading data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import numpy as np

from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)

from ni.protobuf.types.scalar_conversion import scalar_to_protobuf
from ni.protobuf.types.vector_conversion import vector_to_protobuf
from ni.protobuf.types.waveform_conversion import (
    digital_waveform_to_protobuf,
    float64_analog_waveform_to_protobuf,
    float64_complex_waveform_to_protobuf,
    float64_spectrum_to_protobuf,
    int16_analog_waveform_to_protobuf,
    int16_complex_waveform_to_protobuf,
)
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
    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: _TPythonType,
    ) -> None:
        """Populate publish measurement request value."""


class PublishBatchConverter(Generic[_TPythonType], ABC):
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
    def populate_publish_condition_batch_request_values(
        self,
        publish_request: PublishConditionBatchRequest,
        values: _TPythonType,
    ) -> None:
        """Populate publish condition batch request value."""

    @abstractmethod
    def populate_publish_measurement_batch_request_values(
        self,
        publish_request: PublishMeasurementBatchRequest,
        values: _TPythonType,
    ) -> None:
        """Populate publish measurement batch request values."""


class BoolPublishConverter(PublishConverter[bool]):
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

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: bool,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.scalar.bool_value = value


class IntPublishConverter(PublishConverter[int]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return int

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: int,
    ) -> None:
        """Populate publish condition request value."""
        publish_request.scalar.sint32_value = value

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: int,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.scalar.sint32_value = value


class FloatPublishConverter(PublishConverter[float]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return float

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: float,
    ) -> None:
        """Populate publish condition request value."""
        publish_request.scalar.double_value = value

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: float,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.scalar.double_value = value


class StringPublishConverter(PublishConverter[str]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return str

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: str,
    ) -> None:
        """Populate publish condition request value."""
        publish_request.scalar.string_value = value

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: str,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.scalar.string_value = value


class ScalarPublishConverter(PublishConverter[Scalar]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Scalar

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: Scalar,
    ) -> None:
        """Populate publish condition request value."""
        publish_request.scalar.CopyFrom(scalar_to_protobuf(value))

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: Scalar,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.scalar.CopyFrom(scalar_to_protobuf(value))


class VectorPublishConverter(PublishConverter[Vector]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Vector

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: Vector,
    ) -> None:
        """Populate publish condition request value."""
        raise TypeError("Invalid condition request value type: Vector")

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: Vector,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.vector.CopyFrom(vector_to_protobuf(value))


class VectorPublishBatchConverter(PublishBatchConverter[Vector]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Vector

    def populate_publish_condition_batch_request_values(
        self,
        publish_request: PublishConditionBatchRequest,
        values: Vector,
    ) -> None:
        """Populate publish condition batch request value."""
        publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))

    def populate_publish_measurement_batch_request_values(
        self,
        publish_request: PublishMeasurementBatchRequest,
        values: Vector,
    ) -> None:
        """Populate publish measurement batch request values."""
        publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))


class AnalogWaveformPublishConverter(PublishConverter[AnalogWaveform]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return AnalogWaveform

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: AnalogWaveform,
    ) -> None:
        """Populate publish condition request value."""
        raise TypeError("Invalid condition request value type: AnalogWaveform")

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: AnalogWaveform,
    ) -> None:
        """Populate publish measurement request value."""
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


class ComplexWaveformPublishConverter(PublishConverter[ComplexWaveform]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return ComplexWaveform

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: ComplexWaveform,
    ) -> None:
        """Populate publish condition request value."""
        raise TypeError("Invalid condition request value type: AnalogWaveform")

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: ComplexWaveform,
    ) -> None:
        """Populate publish measurement request value."""
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


class SpectrumPublishConverter(PublishConverter[Spectrum]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return Spectrum

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: Spectrum,
    ) -> None:
        """Populate publish condition request value."""
        raise TypeError("Invalid condition request value type: Spectrum")

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: Spectrum,
    ) -> None:
        """Populate publish measurement request value."""
        if value.dtype == np.float64:
            publish_request.double_spectrum.CopyFrom(float64_spectrum_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported Spectrum dtype: {value.dtype}")


class DigitalWaveformPublishConverter(PublishConverter[DigitalWaveform]):
    """A converter for boolean types."""

    @property
    def python_type(self) -> type:
        """The Python type that this converter handles."""
        return DigitalWaveform

    def populate_publish_condition_request_value(
        self,
        publish_request: PublishConditionRequest,
        value: DigitalWaveform,
    ) -> None:
        """Populate publish condition request value."""
        raise TypeError("Invalid condition request value type: DigitalWaveform")

    def populate_publish_measurement_request_value(
        self,
        publish_request: PublishMeasurementRequest,
        value: DigitalWaveform,
    ) -> None:
        """Populate publish measurement request value."""
        publish_request.digital_waveform.CopyFrom(digital_waveform_to_protobuf(value))
