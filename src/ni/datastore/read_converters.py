"""Datastore client for publishing and reading data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Generic, Type, TypeVar

from google.protobuf import any_pb2
from google.protobuf.message import Message

import numpy as np
from google.protobuf.any_pb2 import Any

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
from ni.protobuf.types.xydata_pb2 import DoubleXYData


def unpack_data(read_value: Any) -> object:
    data_type_url = read_value.type_url

    data_type_prefix = "type.googleapis.com/"
    if data_type_url == data_type_prefix + DoubleAnalogWaveform.DESCRIPTOR.full_name:
        double_analog_waveform = DoubleAnalogWaveform()
        read_value.Unpack(double_analog_waveform)
        return double_analog_waveform
    elif data_type_url == data_type_prefix + I16AnalogWaveform.DESCRIPTOR.full_name:
        i16_analog_waveform = I16AnalogWaveform()
        read_value.Unpack(i16_analog_waveform)
        return i16_analog_waveform
    elif data_type_url == data_type_prefix + DoubleComplexWaveform.DESCRIPTOR.full_name:
        double_complex_waveform = DoubleComplexWaveform()
        read_value.Unpack(double_complex_waveform)
        return double_complex_waveform
    elif data_type_url == data_type_prefix + I16ComplexWaveform.DESCRIPTOR.full_name:
        i16_complex_waveform = I16ComplexWaveform()
        read_value.Unpack(i16_complex_waveform)
        return i16_complex_waveform
    elif data_type_url == data_type_prefix + DoubleSpectrum.DESCRIPTOR.full_name:
        spectrum = DoubleSpectrum()
        read_value.Unpack(spectrum)
        return spectrum
    elif data_type_url == data_type_prefix + DigitalWaveformProto.DESCRIPTOR.full_name:
        digital_waveform = DigitalWaveformProto()
        read_value.Unpack(digital_waveform)
        return digital_waveform
    elif data_type_url == data_type_prefix + DoubleXYData.DESCRIPTOR.full_name:
        xydata = DoubleXYData()
        read_value.Unpack(xydata)
        return xydata
    elif data_type_url == data_type_prefix + VectorProto.DESCRIPTOR.full_name:
        vector = VectorProto()
        read_value.Unpack(vector)
        return vector

    else:
        raise TypeError(f"Unsupported data type URL: {data_type_url}")

def convert_from_protobuf(unpacked_data: object) -> object:
    if isinstance(unpacked_data, DoubleAnalogWaveform):
        return float64_analog_waveform_from_protobuf(unpacked_data)
    elif isinstance(unpacked_data, I16AnalogWaveform):
        return int16_analog_waveform_from_protobuf(unpacked_data)
    elif isinstance(unpacked_data, DoubleComplexWaveform):
        return float64_complex_waveform_from_protobuf(unpacked_data)
    elif isinstance(unpacked_data, I16ComplexWaveform):
        return int16_complex_waveform_from_protobuf(unpacked_data)
    elif isinstance(unpacked_data, DoubleSpectrum):
        return float64_spectrum_from_protobuf(unpacked_data)
    elif isinstance(unpacked_data, DigitalWaveformProto):
        return digital_waveform_from_protobuf(unpacked_data)
    elif isinstance(unpacked_data, DoubleXYData):
        return unpacked_data  # TODO: Implement conversion to proper XYData type
    elif isinstance(unpacked_data, VectorProto):
        return vector_from_protobuf(unpacked_data)
    else:
        raise TypeError(f"Unsupported unpacked data type: {type(unpacked_data)}")


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


class VectorReadConverter(ReadConverter[VectorProto]):
    """A converter for DoubleAnalogWaveform types."""

    @property
    def protobuf_message(self) -> Type[VectorProto]:
        """The type-specific protobuf message for the Python type."""
        return VectorProto

    def to_python_value(self, protobuf_message: VectorProto) -> object:
        """Convert the protobuf message to a Python DoubleAnalogWaveform."""
        return vector_from_protobuf(protobuf_message)
