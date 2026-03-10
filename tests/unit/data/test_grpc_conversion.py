import numpy as np
import pytest
from ni.datastore.data._grpc_conversion import (
    populate_publish_condition_batch_request_values,
    populate_publish_condition_request_value,
    populate_publish_measurement_batch_request_values,
    populate_publish_measurement_request_value,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)
from ni.protobuf.types import (
    scalar_pb2,
    vector_pb2,
    waveform_pb2,
    xydata_pb2,
)
from nitypes.complex import ComplexInt32DType
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData


# ========================================================
# Populate Condition
# ========================================================
@pytest.mark.parametrize(
    "python_value, attr_to_check",
    [
        (True, "bool_value"),
        (456.2, "double_value"),
        (123, "sint32_value"),
        ("mystr", "string_value"),
    ],
)
def test___python_builtin_scalar___populate_condition___condition_updated_correctly(
    python_value: object, attr_to_check: str
) -> None:
    request = PublishConditionRequest()
    populate_publish_condition_request_value(request, python_value)

    updated_value = request.scalar.__getattribute__(attr_to_check)
    assert isinstance(updated_value, type(python_value))
    assert updated_value == python_value


def test___python_scalar_object___populate_condition___condition_updated_correctly() -> None:
    scalar_obj = Scalar(1.0, "amps")
    request = PublishConditionRequest()
    populate_publish_condition_request_value(request, scalar_obj)

    assert isinstance(request.scalar, scalar_pb2.Scalar)
    assert request.scalar.double_value == 1.0
    assert request.scalar.attributes["NI_UnitDescription"].string_value == "amps"


# ========================================================
# Populate Condition Batch
# ========================================================
def test___python_vector_object___populate_batch_condition___condition_updated_correctly() -> None:
    vector_obj = Vector([1.0, 2.0, 3.0], "amps")
    request = PublishConditionBatchRequest()
    populate_publish_condition_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"


# ========================================================
# Populate Measurement
# ========================================================
@pytest.mark.parametrize(
    "python_value, attr_to_check",
    [
        (True, "bool_value"),
        (456.2, "double_value"),
        (123, "sint32_value"),
        ("mystr", "string_value"),
    ],
)
def test___python_builtin_scalar___populate_measurement___measurement_updated_correctly(
    python_value: object, attr_to_check: str
) -> None:
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, python_value)

    updated_value = request.scalar.__getattribute__(attr_to_check)
    assert isinstance(updated_value, type(python_value))
    assert updated_value == python_value


def test___python_vector_object___populate_measurement___measurement_updated_correctly() -> None:
    vector_obj = Vector([1.0, 2.0, 3.0], "amps")
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, vector_obj)

    assert isinstance(request.vector, vector_pb2.Vector)
    assert list(request.vector.double_array.values) == [1.0, 2.0, 3.0]
    assert request.vector.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_float64_analog_waveform___populate_measurement___measurement_updated_correctly() -> (
    None
):
    wfm_obj = AnalogWaveform(3, np.float64)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.double_analog_waveform, waveform_pb2.DoubleAnalogWaveform)
    assert list(request.double_analog_waveform.y_data) == [0.0, 0.0, 0.0]


def test___python_int16_analog_waveform___populate_measurement___measurement_updated_correctly() -> (
    None
):
    wfm_obj = AnalogWaveform(3, np.int16)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.i16_analog_waveform, waveform_pb2.I16AnalogWaveform)
    assert list(request.i16_analog_waveform.y_data) == [0, 0, 0]


def test___python_float64_complex_waveform___populate_measurement___measurement_updated_correctly() -> (
    None
):
    wfm_obj = ComplexWaveform(2, np.complex128)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.double_complex_waveform, waveform_pb2.DoubleComplexWaveform)
    assert list(request.double_complex_waveform.y_data) == [0.0, 0.0, 0.0, 0.0]


def test___python_int16_complex_waveform___populate_measurement___measurement_updated_correctly() -> (
    None
):
    wfm_obj = ComplexWaveform(2, ComplexInt32DType)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.i16_complex_waveform, waveform_pb2.I16ComplexWaveform)
    assert list(request.i16_complex_waveform.y_data) == [0, 0, 0, 0]


def test___python_bool_digital_waveform___populate_measurement___measurement_updated_correctly() -> (
    None
):
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    wfm_obj = DigitalWaveform.from_lines(data, signal_count=3)

    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.digital_waveform, waveform_pb2.DigitalWaveform)
    assert request.digital_waveform.y_data == b"\x00\x01\x00\x01\x00\x01"
    assert request.digital_waveform.signal_count == 3


def test___python_uint8_digital_waveform___populate_measurement___measurement_updated_correctly() -> (
    None
):
    data = np.array([[0, 1, 3], [7, 5, 1]], dtype=np.uint8)
    wfm_obj = DigitalWaveform.from_lines(data, signal_count=3)

    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.digital_waveform, waveform_pb2.DigitalWaveform)
    assert request.digital_waveform.y_data == b"\x00\x01\x03\x07\x05\x01"
    assert request.digital_waveform.signal_count == 3


def test___python_float64_spectrum___populate_measurement___measurement_updated_correctly() -> None:
    spectrum = Spectrum.from_array_1d(np.array([1.0, 2.0, 3.0]))
    spectrum.start_frequency = 100.0
    spectrum.frequency_increment = 10.0

    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, spectrum)

    assert isinstance(request.double_spectrum, waveform_pb2.DoubleSpectrum)
    assert list(request.double_spectrum.data) == [1.0, 2.0, 3.0]
    assert request.double_spectrum.start_frequency == 100.0
    assert request.double_spectrum.frequency_increment == 10.0


def test___python_float64_xydata___populate_measurement___measurement_updated_correctly() -> None:
    xydata = XYData.from_arrays_1d(
        [1.0, 2.0], [3.0, 4.0], np.float64, x_units="Volts", y_units="Seconds"
    )

    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, xydata)

    assert isinstance(request.x_y_data, xydata_pb2.DoubleXYData)
    assert list(request.x_y_data.x_data) == [1.0, 2.0]
    assert list(request.x_y_data.y_data) == [3.0, 4.0]
    assert request.x_y_data.attributes["NI_UnitDescription_X"].string_value == "Volts"
    assert request.x_y_data.attributes["NI_UnitDescription_Y"].string_value == "Seconds"


# ========================================================
# Populate Measurement Batch
# ========================================================
def test___python_vector_object___populate_measurement_batch___condition_updated_correctly() -> (
    None
):
    vector_obj = Vector([1.0, 2.0, 3.0], "amps")
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"
