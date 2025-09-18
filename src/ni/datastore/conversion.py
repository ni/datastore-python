"""Datastore client for publishing and reading data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Generic, Type, TypeVar

from google.protobuf import any_pb2

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

_READ_CONVERTERS: list[ReadConverter] = [
    DoubleAnalogWaveformReadConverter(),
    DoubleComplexWaveformReadConverter(),
    DoubleSpectrumReadConverter(),
    DigitalWaveformReadConverter(),
    I16AnalogWaveformReadConverter(),
    I16ComplexWaveformReadConverter(),
    VectorReadConverter(),
]

_CONVERTER_FOR_GRPC_TYPE = {entry.protobuf_typename: entry for entry in _READ_CONVERTERS}


def from_any(protobuf_any: any_pb2.Any) -> object:
    """Convert a protobuf Any to a Python object."""
    if not isinstance(protobuf_any, any_pb2.Any):
        raise ValueError(f"Unexpected type: {type(protobuf_any)}")

    underlying_typename = protobuf_any.TypeName()

    converter = _CONVERTER_FOR_GRPC_TYPE[underlying_typename]
    return converter.to_python(protobuf_any)


