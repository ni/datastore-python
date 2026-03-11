"""Contains tests to validate the data store client read functionality."""

from __future__ import annotations

from unittest.mock import Mock, NonCallableMock

import numpy as np
import pytest
from ni.datastore.data import DataStoreClient, PublishedCondition, PublishedMeasurement
from ni.protobuf.types import (
    array_pb2,
    attribute_value_pb2,
    vector_pb2,
    waveform_pb2,
    xydata_pb2,
)
from nitypes.complex import ComplexInt32DType
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData


def test___read_data_measurement___calls_data_store_client(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-123")
    expected_waveform = waveform_pb2.DoubleAnalogWaveform(y_data=[1.0, 2.0, 3.0])
    response = Mock()
    response.WhichOneof.return_value = "double_analog_waveform"
    response.double_analog_waveform = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, AnalogWaveform)

    mocked_data_store_service_client.read_measurement_value.assert_called_once()
    args, __ = mocked_data_store_service_client.read_measurement_value.call_args
    request = args[0]
    assert request.measurement_id == "measurement-123"
    assert isinstance(actual_waveform, AnalogWaveform)
    assert list(actual_waveform.scaled_data) == list(expected_waveform.y_data)


def test___read_double_analog_waveform___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-123")
    expected_waveform = waveform_pb2.DoubleAnalogWaveform(y_data=[1.0, 2.0, 3.0])
    response = Mock()
    response.WhichOneof.return_value = "double_analog_waveform"
    response.double_analog_waveform = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, AnalogWaveform)

    assert isinstance(actual_waveform, AnalogWaveform)
    assert list(actual_waveform.scaled_data) == list(expected_waveform.y_data)


def test___read_i16_analog_waveform___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-456")
    expected_waveform = waveform_pb2.I16AnalogWaveform(y_data=[1, 2, 3])
    response = Mock()
    response.WhichOneof.return_value = "i16_analog_waveform"
    response.i16_analog_waveform = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, AnalogWaveform)

    assert isinstance(actual_waveform, AnalogWaveform)
    assert list(actual_waveform.raw_data) == list(expected_waveform.y_data)


def test___read_double_complex_waveform___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-789")
    expected_waveform = waveform_pb2.DoubleComplexWaveform(y_data=[1.0, 2.0, 3.0, 4.0])
    response = Mock()
    response.WhichOneof.return_value = "double_complex_waveform"
    response.double_complex_waveform = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, ComplexWaveform)

    assert isinstance(actual_waveform, ComplexWaveform)
    assert actual_waveform.sample_count == actual_waveform.capacity == 2
    assert len(actual_waveform.raw_data) == 2
    assert actual_waveform.dtype == np.complex128


def test___read_i16_complex_waveform___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-101")
    expected_waveform = waveform_pb2.I16ComplexWaveform(y_data=[1, 2, 3, 4])
    response = Mock()
    response.WhichOneof.return_value = "i16_complex_waveform"
    response.i16_complex_waveform = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, ComplexWaveform)

    assert isinstance(actual_waveform, ComplexWaveform)
    assert actual_waveform.sample_count == actual_waveform.capacity == 2
    assert len(actual_waveform.raw_data) == 2
    assert actual_waveform.dtype == ComplexInt32DType


def test___read_digital_waveform___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-202")
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    expected_waveform = waveform_pb2.DigitalWaveform(y_data=data.tobytes(), signal_count=3)
    response = Mock()
    response.WhichOneof.return_value = "digital_waveform"
    response.digital_waveform = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, DigitalWaveform)

    assert isinstance(actual_waveform, DigitalWaveform)
    assert np.array_equal(actual_waveform.data, data)
    assert actual_waveform.signal_count == 3


def test___read_double_spectrum___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-303")
    expected_waveform = waveform_pb2.DoubleSpectrum(
        data=[1.0, 2.0, 3.0],
        start_frequency=100.0,
        frequency_increment=10.0,
    )
    response = Mock()
    response.WhichOneof.return_value = "double_spectrum"
    response.double_spectrum = expected_waveform
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_waveform = data_store_client.read_data(published_measurement, Spectrum)

    assert isinstance(actual_waveform, Spectrum)
    assert list(actual_waveform.data) == [1.0, 2.0, 3.0]
    assert actual_waveform.start_frequency == 100.0
    assert actual_waveform.frequency_increment == 10.0


def test___read_vector___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-404")
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="amps")}
    expected_vector = vector_pb2.Vector(
        attributes=attrs,
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    response = Mock()
    response.WhichOneof.return_value = "vector"
    response.vector = expected_vector
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_vector = data_store_client.read_data(published_measurement, Vector)

    assert isinstance(actual_vector, Vector)
    assert list(actual_vector) == [1.0, 2.0, 3.0]
    assert actual_vector.units == "amps"


def test___read_xydata___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-505")
    attrs = {
        "NI_UnitDescription_X": attribute_value_pb2.AttributeValue(string_value="amps"),
        "NI_UnitDescription_Y": attribute_value_pb2.AttributeValue(string_value="seconds"),
    }
    expected_xydata = xydata_pb2.DoubleXYData(
        x_data=[1.0, 2.0],
        y_data=[3.0, 4.0],
        attributes=attrs,
    )
    response = Mock()
    response.WhichOneof.return_value = "x_y_data"
    response.x_y_data = expected_xydata
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_xydata = data_store_client.read_data(published_measurement, XYData)

    assert isinstance(actual_xydata, XYData)
    assert list(actual_xydata.x_data) == [1.0, 2.0]
    assert list(actual_xydata.y_data) == [3.0, 4.0]
    assert actual_xydata.x_units == "amps"
    assert actual_xydata.y_units == "seconds"


def test___read_condition___value_correct(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_condition = PublishedCondition(id="condition-789")
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="volts")}
    expected_vector = vector_pb2.Vector(
        attributes=attrs,
        double_array=array_pb2.DoubleArray(values=[5.0, 6.0, 7.0]),
    )
    response = Mock()
    response.WhichOneof.return_value = "vector"
    response.vector = expected_vector
    mocked_data_store_service_client.read_condition_value.return_value = response

    actual_vector = data_store_client.read_data(published_condition, Vector)

    mocked_data_store_service_client.read_condition_value.assert_called_once()
    args, __ = mocked_data_store_service_client.read_condition_value.call_args
    request = args[0]
    assert request.condition_id == "condition-789"
    assert isinstance(actual_vector, Vector)
    assert list(actual_vector) == [5.0, 6.0, 7.0]
    assert actual_vector.units == "volts"


def test___read_data___without_expected_type___returns_object(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-999")
    expected_vector = vector_pb2.Vector(
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    response = Mock()
    response.WhichOneof.return_value = "vector"
    response.vector = expected_vector
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_value = data_store_client.read_data(published_measurement)

    # Without expected_type, it returns the converted Python object
    assert isinstance(actual_value, Vector)
    assert list(actual_value) == [1.0, 2.0, 3.0]


def test___read_data___with_matching_expected_type___returns_typed_value(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-888")
    expected_vector = vector_pb2.Vector(
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    response = Mock()
    response.WhichOneof.return_value = "vector"
    response.vector = expected_vector
    mocked_data_store_service_client.read_measurement_value.return_value = response

    actual_value = data_store_client.read_data(published_measurement, Vector)

    assert isinstance(actual_value, Vector)
    assert list(actual_value) == [1.0, 2.0, 3.0]


def test___read_data___with_mismatched_expected_type___raises_type_error(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-777")
    expected_vector = vector_pb2.Vector(
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    response = Mock()
    response.WhichOneof.return_value = "vector"
    response.vector = expected_vector
    mocked_data_store_service_client.read_measurement_value.return_value = response

    with pytest.raises(TypeError, match="Expected type.*AnalogWaveform.*got"):
        data_store_client.read_data(published_measurement, AnalogWaveform)


def test___read_measurement___unsupported_type___raises_type_error(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_measurement = PublishedMeasurement(id="measurement-666")
    response = Mock()
    response.WhichOneof.return_value = "unknown_type"
    mocked_data_store_service_client.read_measurement_value.return_value = response

    with pytest.raises(TypeError, match="Invalid read type: unknown_type"):
        data_store_client.read_data(published_measurement)


def test___read_condition___unsupported_type___raises_type_error(
    data_store_client: DataStoreClient, mocked_data_store_service_client: NonCallableMock
) -> None:
    published_condition = PublishedCondition(id="condition-555")
    response = Mock()
    response.WhichOneof.return_value = "unknown_type"
    mocked_data_store_service_client.read_condition_value.return_value = response

    with pytest.raises(TypeError, match="Invalid read type: unknown_type"):
        data_store_client.read_data(published_condition)
