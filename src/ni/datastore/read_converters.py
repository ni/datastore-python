"""Datastore client for publishing and reading data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from google.protobuf import any_pb2
from google.protobuf.message import Message
from ni.protobuf.types.scalar_conversion import scalar_from_protobuf
from ni.protobuf.types.scalar_pb2 import Scalar as ScalarProto
from ni.protobuf.types.vector_conversion import vector_from_protobuf
from ni.protobuf.types.vector_pb2 import Vector as VectorProto
from ni.protobuf.types.waveform_conversion import (
    digital_waveform_from_protobuf,
    float64_analog_waveform_from_protobuf,
    float64_complex_waveform_from_protobuf,
    float64_spectrum_from_protobuf,
    int16_analog_waveform_from_protobuf,
    int16_complex_waveform_from_protobuf,
)
from ni.protobuf.types.waveform_pb2 import (
    DigitalWaveform as DigitalWaveformProto,
    DoubleAnalogWaveform,
    DoubleComplexWaveform,
    DoubleSpectrum,
    I16AnalogWaveform,
    I16ComplexWaveform,
)


_TProtobufType = TypeVar("_TProtobufType", bound=Message)


class ReadConverter(Generic[_TProtobufType], ABC):
    """A class that defines how to convert between Python objects and protobuf Any messages."""

    @property
    @abstractmethod
    def protobuf_message(self) -> Type[_TProtobufType]:
        """The type-specific protobuf message for the Python type."""

    @property
    def protobuf_typename(self) -> str:
        """The protobuf name for the type."""
        return self.protobuf_message.DESCRIPTOR.full_name  # type: ignore[no-any-return]

    def to_python(self, protobuf_value: any_pb2.Any) -> object:
        """Convert the protobuf Any message to its matching Python type."""
        protobuf_message = self.protobuf_message()
        did_unpack = protobuf_value.Unpack(protobuf_message)
        if not did_unpack:
            raise ValueError(f"Failed to unpack Any with type '{protobuf_value.TypeName()}'")
        return self.to_python_value(protobuf_message)

    @abstractmethod
    def to_python_value(self, protobuf_message: _TProtobufType) -> object:
        """Convert the protobuf wrapper message to its matching Python type."""


class DoubleAnalogWaveformReadConverter(ReadConverter[DoubleAnalogWaveform]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[DoubleAnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return DoubleAnalogWaveform

    def to_python_value(self, protobuf_message: DoubleAnalogWaveform) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return float64_analog_waveform_from_protobuf(protobuf_message)


class I16AnalogWaveformReadConverter(ReadConverter[I16AnalogWaveform]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[I16AnalogWaveform]:
        """The type-specific protobuf message for the Python type."""
        return I16AnalogWaveform

    def to_python_value(self, protobuf_message: I16AnalogWaveform) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return int16_analog_waveform_from_protobuf(protobuf_message)


class DoubleComplexWaveformReadConverter(ReadConverter[DoubleComplexWaveform]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[DoubleComplexWaveform]:
        """The type-specific protobuf message for the Python type."""
        return DoubleComplexWaveform

    def to_python_value(self, protobuf_message: DoubleComplexWaveform) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return float64_complex_waveform_from_protobuf(protobuf_message)


class I16ComplexWaveformReadConverter(ReadConverter[I16ComplexWaveform]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[I16ComplexWaveform]:
        """The type-specific protobuf message for the Python type."""
        return I16ComplexWaveform

    def to_python_value(self, protobuf_message: I16ComplexWaveform) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return int16_complex_waveform_from_protobuf(protobuf_message)


class DoubleSpectrumReadConverter(ReadConverter[DoubleSpectrum]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[DoubleSpectrum]:
        """The type-specific protobuf message for the Python type."""
        return DoubleSpectrum

    def to_python_value(self, protobuf_message: DoubleSpectrum) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return float64_spectrum_from_protobuf(protobuf_message)


class DigitalWaveformReadConverter(ReadConverter[DigitalWaveformProto]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[DigitalWaveformProto]:
        """The type-specific protobuf message for the Python type."""
        return DigitalWaveformProto

    def to_python_value(self, protobuf_message: DigitalWaveformProto) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return digital_waveform_from_protobuf(protobuf_message)


class ScalarReadConverter(ReadConverter[ScalarProto]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[ScalarProto]:
        """The type-specific protobuf message for the Python type."""
        return ScalarProto

    def to_python_value(self, protobuf_message: ScalarProto) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return scalar_from_protobuf(protobuf_message)


class VectorReadConverter(ReadConverter[VectorProto]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[VectorProto]:
        """The type-specific protobuf message for the Python type."""
        return VectorProto

    def to_python_value(self, protobuf_message: VectorProto) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return vector_from_protobuf(protobuf_message)
