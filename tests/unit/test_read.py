"""Contains tests to validate the datastore client read functionality."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock

import numpy as np
from google.protobuf.any_pb2 import Any as gpAny
from ni.datamonikers.v1.data_moniker_pb2 import Moniker, ReadFromMonikerResult
from ni.datastore import Client
from ni.protobuf.types import array_pb2, attribute_value_pb2, vector_pb2, waveform_pb2
from nitypes.complex import ComplexInt32DType
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum


def test___read_data___calls_monikerclient(client: Client, mocked_moniker_client: Mock) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    expected_waveform = waveform_pb2.DoubleAnalogWaveform(y_data=[1.0, 2.0, 3.0])
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, AnalogWaveform)

    args, __ = mocked_moniker_client.read_from_moniker.call_args
    requested_moniker = cast(Moniker, args[0])
    assert requested_moniker.service_location == moniker.service_location
    assert requested_moniker.data_instance == moniker.data_instance
    assert requested_moniker.data_source == moniker.data_source
    assert isinstance(actual_waveform, AnalogWaveform)
    assert list(actual_waveform.scaled_data) == list(expected_waveform.y_data)


def test___read_double_analog_waveform___value_correct(
    client: Client, mocked_moniker_client: Mock
) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    expected_waveform = waveform_pb2.DoubleAnalogWaveform(y_data=[1.0, 2.0, 3.0])
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, AnalogWaveform)

    assert isinstance(actual_waveform, AnalogWaveform)
    assert list(actual_waveform.scaled_data) == list(expected_waveform.y_data)


def test___read_i16_analog_waveform___value_correct(
    client: Client, mocked_moniker_client: Mock
) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    expected_waveform = waveform_pb2.I16AnalogWaveform(y_data=[1, 2, 3])
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, AnalogWaveform)

    assert isinstance(actual_waveform, AnalogWaveform)
    assert list(actual_waveform.raw_data) == list(expected_waveform.y_data)


def test___read_double_complex_waveform___value_correct(
    client: Client, mocked_moniker_client: Mock
) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    expected_waveform = waveform_pb2.DoubleComplexWaveform(y_data=[1.0, 2.0, 3.0, 4.0])
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, ComplexWaveform)

    assert isinstance(actual_waveform, ComplexWaveform)
    assert actual_waveform.sample_count == actual_waveform.capacity == 2
    assert len(actual_waveform.raw_data) == 2
    assert actual_waveform.dtype == np.complex128


def test___read_i16_complex_waveform___value_correct(
    client: Client, mocked_moniker_client: Mock
) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    expected_waveform = waveform_pb2.I16ComplexWaveform(y_data=[1, 2, 3, 4])
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, ComplexWaveform)

    assert isinstance(actual_waveform, ComplexWaveform)
    assert actual_waveform.sample_count == actual_waveform.capacity == 2
    assert len(actual_waveform.raw_data) == 2
    assert actual_waveform.dtype == ComplexInt32DType


def test___read_digital_waveform___value_correct(
    client: Client, mocked_moniker_client: Mock
) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    expected_waveform = waveform_pb2.DigitalWaveform(y_data=data.tobytes(), signal_count=3)
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, DigitalWaveform)

    assert isinstance(actual_waveform, DigitalWaveform)
    assert np.array_equal(actual_waveform.data, data)
    assert actual_waveform.signal_count == 3


def test___read_double_spectrum___value_correct(
    client: Client, mocked_moniker_client: Mock
) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    expected_waveform = waveform_pb2.DoubleSpectrum(
        data=[1.0, 2.0, 3.0],
        start_frequency=100.0,
        frequency_increment=10.0,
    )
    value_to_read.Pack(expected_waveform)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_waveform = client.read_data(moniker, Spectrum)

    assert isinstance(actual_waveform, Spectrum)
    assert list(actual_waveform.data) == [1.0, 2.0, 3.0]
    assert actual_waveform.start_frequency == 100.0
    assert actual_waveform.frequency_increment == 10.0


def test___read_vector___value_correct(client: Client, mocked_moniker_client: Mock) -> None:
    moniker = _init_moniker()
    result = ReadFromMonikerResult()
    value_to_read = gpAny()
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="amps")}
    expected_vector = vector_pb2.Vector(
        attributes=attrs,
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    value_to_read.Pack(expected_vector)
    result.value.CopyFrom(value_to_read)
    mocked_moniker_client.read_from_moniker.return_value = result

    actual_vector = client.read_data(moniker, Vector)

    assert isinstance(actual_vector, Vector)
    assert list(actual_vector) == [1.0, 2.0, 3.0]
    assert actual_vector.units == "amps"


def _init_moniker() -> Moniker:
    moniker = Moniker()
    moniker.data_instance = 12
    moniker.data_source = "ABCD123"
    moniker.service_location = "http://localhost:50051"
    return moniker
