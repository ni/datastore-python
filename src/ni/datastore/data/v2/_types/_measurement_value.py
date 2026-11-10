"""Measurement value types for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeAlias, Union

from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData

from ni.datastore.data.v2._types._json_value import JsonValue

MeasurementReadValue: TypeAlias = Union[
    Scalar[Any],
    Vector[Any],
    AnalogWaveform[Any],
    ComplexWaveform[Any],
    Spectrum[Any],
    DigitalWaveform[Any],
    XYData[Any],
    dict[str, Any],
    JsonValue,
]
"""A measurement value or limit read from the data store.

A single value is always read as a Scalar and a list of values as a Vector. JSON
is read as a dictionary, or as a JsonValue when it has attributes or a schema.
"""

MeasurementValue: TypeAlias = Union[
    bool,
    int,
    float,
    str,
    MeasurementReadValue,
    Mapping[str, Any],
    Iterable[Union[bool, int, float, str]],
]
"""A measurement value or limit that can be written to the data store.

Includes everything that can be read, plus plain bool, int, float, and str
values, JSON mappings, and lists of plain values.
"""
