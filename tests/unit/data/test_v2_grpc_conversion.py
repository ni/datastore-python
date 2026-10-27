"""Tests for V2 measurement value conversion."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from ni.measurements.data.v2 import data_store_pb2
from nitypes.complex import ComplexInt32DType
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData
from pytest_mock import MockerFixture

from ni.datastore.data.v2 import DataStoreClient
from ni.datastore.data.v2._grpc_conversion import (
    convert_measurement_value_from_protobuf,
    measurement_value_to_protobuf,
)


def _data(value: Any) -> object:
    if isinstance(value, (AnalogWaveform, ComplexWaveform)):
        return value.raw_data.tolist()
    if isinstance(value, Spectrum):
        return value.data.tolist()
    if isinstance(value, DigitalWaveform):
        return value.data.tolist()
    return [value.x_data.tolist(), value.y_data.tolist()]


@pytest.mark.parametrize(
    ("value", "oneof_field"),
    [
        (
            AnalogWaveform.from_array_1d(np.array([1.0, 2.0], np.float64), dtype=np.float64),
            "double_analog_waveform",
        ),
        (
            AnalogWaveform.from_array_1d(np.array([1.0, 2.0], np.float32), dtype=np.float32),
            "float_analog_waveform",
        ),
        (
            AnalogWaveform.from_array_1d(np.array([1, 2], np.int16), dtype=np.int16),
            "i16_analog_waveform",
        ),
        (
            ComplexWaveform.from_array_1d(np.array([1 + 2j], np.complex128), dtype=np.complex128),
            "double_complex_waveform",
        ),
        (
            ComplexWaveform.from_array_1d(np.array([1 + 2j], np.complex64), dtype=np.complex64),
            "float_complex_waveform",
        ),
        (
            ComplexWaveform.from_array_1d(
                np.array([(1, 2), (3, 4)], ComplexInt32DType), dtype=ComplexInt32DType
            ),
            "i16_complex_waveform",
        ),
        (
            Spectrum.from_array_1d(np.array([1.0, 2.0], np.float64), dtype=np.float64),
            "double_spectrum",
        ),
        (
            Spectrum.from_array_1d(np.array([1.0, 2.0], np.float32), dtype=np.float32),
            "float_spectrum",
        ),
        (DigitalWaveform.from_lines([[0, 1], [1, 0]], signal_count=2), "digital_waveform"),
        (XYData.from_arrays_1d([1.0, 2.0], [3.0, 4.0], np.float64), "x_y_data"),
    ],
)
def test___waveform_family_value___round_trips_with_matching_type_and_dtype(
    value: Any, oneof_field: str
) -> None:
    proto = measurement_value_to_protobuf(value)

    assert proto is not None
    assert proto.WhichOneof("value") == oneof_field
    read_back: Any = convert_measurement_value_from_protobuf(proto)
    assert type(read_back) is type(value)
    assert read_back.dtype == value.dtype
    assert _data(read_back) == _data(value)


@pytest.mark.parametrize(
    "value",
    [
        AnalogWaveform.from_array_1d(np.array([1, 2], np.int32), dtype=np.int32),
        Spectrum.from_array_1d(np.array([1, 2], np.int32), dtype=np.int32),
        XYData.from_arrays_1d([1.0, 2.0], [3.0, 4.0], np.float32),
    ],
)
def test___unsupported_dtype___raises_type_error(value: Any) -> None:
    with pytest.raises(TypeError, match="Unsupported"):
        measurement_value_to_protobuf(value)


def test___create_measurement_with_unsupported_dtype___raises_before_rpc(
    mocker: MockerFixture,
) -> None:
    service_client = mocker.Mock()
    mocker.patch(
        "ni.datastore.data.v2._data_store_client.DataStoreServiceClient",
        return_value=service_client,
    )
    value = AnalogWaveform.from_array_1d(np.array([1, 2], np.int32), dtype=np.int32)

    with pytest.raises(TypeError):
        DataStoreClient().create_measurement("voltage", value, "step-id")

    service_client.create_measurement.assert_not_called()


def test___missing_value___raises_type_error() -> None:
    with pytest.raises(TypeError):
        convert_measurement_value_from_protobuf(data_store_pb2.MeasurementValue())
