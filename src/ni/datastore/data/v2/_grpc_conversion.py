"""Conversion helpers for V2 measurement values."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, cast

import hightime as ht
import numpy as np
from google.protobuf import json_format
from google.protobuf.message import Message
from google.protobuf.struct_pb2 import Struct
from ni.measurements.data.v2.data_store_pb2 import MeasurementValue
from ni.protobuf.types.precision_duration_conversion import (
    hightime_timedelta_from_protobuf,
    hightime_timedelta_to_protobuf,
)
from ni.protobuf.types.precision_duration_pb2 import PrecisionDuration
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_from_protobuf,
    hightime_datetime_to_protobuf,
)
from ni.protobuf.types.precision_timestamp_pb2 import PrecisionTimestamp
from ni.protobuf.types.scalar_conversion import scalar_from_protobuf, scalar_to_protobuf
from ni.protobuf.types.vector_conversion import vector_from_protobuf, vector_to_protobuf
from ni.protobuf.types.waveform_conversion import (
    digital_waveform_from_protobuf,
    digital_waveform_to_protobuf,
    float32_analog_waveform_from_protobuf,
    float32_analog_waveform_to_protobuf,
    float32_complex_waveform_from_protobuf,
    float32_complex_waveform_to_protobuf,
    float32_spectrum_from_protobuf,
    float32_spectrum_to_protobuf,
    float64_analog_waveform_from_protobuf,
    float64_analog_waveform_to_protobuf,
    float64_complex_waveform_from_protobuf,
    float64_complex_waveform_to_protobuf,
    float64_spectrum_from_protobuf,
    float64_spectrum_to_protobuf,
    int16_analog_waveform_from_protobuf,
    int16_analog_waveform_to_protobuf,
    int16_complex_waveform_from_protobuf,
    int16_complex_waveform_to_protobuf,
)
from ni.protobuf.types.xydata_conversion import (
    float64_xydata_from_protobuf,
    float64_xydata_to_protobuf,
)
from nitypes.complex import ComplexInt32DType
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData

from ni.datastore.data.v2._types._json_value import JsonValue, json_value_from_protobuf


def populate_measurement_value(measurement_value: MeasurementValue, value: object) -> None:
    """Convert a supported Python value into a V2 measurement value."""
    if isinstance(value, bool):
        measurement_value.scalar.bool_value = value
    elif isinstance(value, int):
        measurement_value.scalar.sint32_value = value
    elif isinstance(value, float):
        measurement_value.scalar.double_value = value
    elif isinstance(value, str):
        measurement_value.scalar.string_value = value
    elif isinstance(value, Scalar):
        measurement_value.scalar.CopyFrom(scalar_to_protobuf(value))
    elif isinstance(value, Vector):
        measurement_value.vector.CopyFrom(vector_to_protobuf(value))
    elif isinstance(value, AnalogWaveform):
        if value.dtype == np.float64:
            measurement_value.double_analog_waveform.CopyFrom(
                float64_analog_waveform_to_protobuf(value)
            )
        elif value.dtype == np.float32:
            measurement_value.float_analog_waveform.CopyFrom(
                float32_analog_waveform_to_protobuf(value)
            )
        elif value.dtype == np.int16:
            measurement_value.i16_analog_waveform.CopyFrom(int16_analog_waveform_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported AnalogWaveform dtype: {value.dtype}")
    elif isinstance(value, ComplexWaveform):
        if value.dtype == np.complex128:
            measurement_value.double_complex_waveform.CopyFrom(
                float64_complex_waveform_to_protobuf(value)
            )
        elif value.dtype == np.complex64:
            measurement_value.float_complex_waveform.CopyFrom(
                float32_complex_waveform_to_protobuf(value)
            )
        elif value.dtype == ComplexInt32DType:
            measurement_value.i16_complex_waveform.CopyFrom(
                int16_complex_waveform_to_protobuf(value)
            )
        else:
            raise TypeError(f"Unsupported ComplexWaveform dtype: {value.dtype}")
    elif isinstance(value, Spectrum):
        if value.dtype == np.float64:
            measurement_value.double_spectrum.CopyFrom(float64_spectrum_to_protobuf(value))
        elif value.dtype == np.float32:
            measurement_value.float_spectrum.CopyFrom(float32_spectrum_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported Spectrum dtype: {value.dtype}")
    elif isinstance(value, DigitalWaveform):
        measurement_value.digital_waveform.CopyFrom(digital_waveform_to_protobuf(value))
    elif isinstance(value, XYData):
        if value.dtype != np.float64:
            raise TypeError(f"Unsupported XYData dtype: {value.dtype}")
        measurement_value.x_y_data.CopyFrom(float64_xydata_to_protobuf(value))
    elif isinstance(value, JsonValue):
        measurement_value.json_value.CopyFrom(value.to_protobuf())
    elif isinstance(value, Mapping):
        json_format.ParseDict(cast(dict[str, Any], dict(value)), measurement_value.json_value.value)
    elif isinstance(value, Iterable):
        try:
            vector = Vector(cast(Iterable[bool | int | float | str], value))
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "Iterable measurement values must contain only bool, int, float, or str values."
            ) from exc
        measurement_value.vector.CopyFrom(vector_to_protobuf(vector))
    else:
        raise TypeError(
            f"Unsupported measurement value type: {type(value)}. Please consult the documentation."
        )


def convert_measurement_value_from_protobuf(measurement_value: MeasurementValue) -> object:
    """Convert a V2 measurement value into a useful Python value."""
    value_type = measurement_value.WhichOneof("value")
    if value_type == "scalar":
        return scalar_from_protobuf(measurement_value.scalar)
    if value_type == "vector":
        return vector_from_protobuf(measurement_value.vector)
    if value_type == "double_analog_waveform":
        return float64_analog_waveform_from_protobuf(measurement_value.double_analog_waveform)
    if value_type == "float_analog_waveform":
        return float32_analog_waveform_from_protobuf(measurement_value.float_analog_waveform)
    if value_type == "i16_analog_waveform":
        return int16_analog_waveform_from_protobuf(measurement_value.i16_analog_waveform)
    if value_type == "double_complex_waveform":
        return float64_complex_waveform_from_protobuf(measurement_value.double_complex_waveform)
    if value_type == "float_complex_waveform":
        return float32_complex_waveform_from_protobuf(measurement_value.float_complex_waveform)
    if value_type == "i16_complex_waveform":
        return int16_complex_waveform_from_protobuf(measurement_value.i16_complex_waveform)
    if value_type == "double_spectrum":
        return float64_spectrum_from_protobuf(measurement_value.double_spectrum)
    if value_type == "float_spectrum":
        return float32_spectrum_from_protobuf(measurement_value.float_spectrum)
    if value_type == "digital_waveform":
        return digital_waveform_from_protobuf(measurement_value.digital_waveform)
    if value_type == "x_y_data":
        return float64_xydata_from_protobuf(measurement_value.x_y_data)
    if value_type == "json_value":
        return json_value_from_protobuf(measurement_value.json_value)
    raise TypeError(f"Unsupported or missing measurement value type: {value_type}.")


def measurement_value_to_protobuf(value: object) -> MeasurementValue | None:
    """Convert an optional measurement value, upper limit, or lower limit to protobuf."""
    if value is None:
        return None
    measurement_value = MeasurementValue()
    populate_measurement_value(measurement_value, value)
    return measurement_value


def measurement_value_from_protobuf(message: Message, field: str) -> object:
    """Convert an optional MeasurementValue field, or return None when it has no inline value."""
    if not message.HasField(field):
        return None
    measurement_value = cast(MeasurementValue, getattr(message, field))
    # Non-scalar payloads may be returned only as a data_moniker reference.
    if measurement_value.WhichOneof("value") in (None, "data_moniker"):
        return None
    return convert_measurement_value_from_protobuf(measurement_value)


def timestamp_to_protobuf(value: ht.datetime | None) -> PrecisionTimestamp | None:
    """Convert an optional hightime datetime to a PrecisionTimestamp."""
    return hightime_datetime_to_protobuf(value) if value is not None else None


def timestamp_from_protobuf(message: Message, field: str) -> ht.datetime | None:
    """Convert an optional PrecisionTimestamp field to a hightime datetime."""
    if not message.HasField(field):
        return None
    return hightime_datetime_from_protobuf(getattr(message, field))


def duration_to_protobuf(value: ht.timedelta | None) -> PrecisionDuration | None:
    """Convert an optional hightime timedelta to a PrecisionDuration."""
    return hightime_timedelta_to_protobuf(value) if value is not None else None


def duration_from_protobuf(message: Message, field: str) -> ht.timedelta | None:
    """Convert an optional PrecisionDuration field to a hightime timedelta."""
    if not message.HasField(field):
        return None
    return hightime_timedelta_from_protobuf(getattr(message, field))


def extension_to_protobuf(value: Mapping[str, Any]) -> Struct | None:
    """Convert an extension mapping to a protobuf Struct, or None when empty."""
    if not value:
        return None
    struct = Struct()
    json_format.ParseDict(dict(value), struct)
    return struct


def extension_from_protobuf(value: Struct) -> dict[str, Any]:
    """Convert a protobuf Struct extension to a Python dictionary."""
    return json_format.MessageToDict(value)
