import numpy as np
import pytest
from google.protobuf import any_pb2
from google.protobuf.message import Message
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)
from ni.protobuf.types import (
    array_pb2,
    attribute_value_pb2,
    scalar_pb2,
    vector_pb2,
    waveform_pb2,
)
from nitypes.complex import ComplexInt32DType
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum

from ni.datastore.conversion import (
    convert_from_protobuf,
    populate_publish_condition_request_value,
    populate_publish_condition_batch_request_values,
    populate_publish_measurement_request_value,
    populate_publish_measurement_batch_request_values,
    _get_type_string,
)


# ========================================================
# _get_type_string() tests
# ========================================================
@pytest.mark.parametrize(
    "python_object, expected_type_string",
    [
        (False, "builtins.bool"),
        (b"mystr", "builtins.bytes"),
        (456.2, "builtins.float"),
        (123, "builtins.int"),
        ("mystr", "builtins.str"),
        (AnalogWaveform(0, np.int16), "nitypes.waveform.AnalogWaveform"),
        (AnalogWaveform(0, np.float64), "nitypes.waveform.AnalogWaveform"),
        (ComplexWaveform(0, np.complex128), "nitypes.waveform.ComplexWaveform"),
        (ComplexWaveform(0, ComplexInt32DType), "nitypes.waveform.ComplexWaveform"),
        (DigitalWaveform(10, 2, np.bool, False), "nitypes.waveform.DigitalWaveform"),
        (Spectrum(10, np.float64), "nitypes.waveform.Spectrum"),
        (Scalar("one"), "nitypes.scalar.Scalar"),
        (Vector([1, 2, 3]), "nitypes.vector.Vector"),
    ],
)
def test___various_python_objects___get_type_string___returns_correct_type_string(
    python_object: object, expected_type_string: str
) -> None:
    type_string = _get_type_string(python_object)
    assert type_string == expected_type_string


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


def test___python_float64_analog_waveform___populate_measurement___measurement_updated_correctly() -> None:
    wfm_obj = AnalogWaveform(3, np.float64)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.double_analog_waveform, waveform_pb2.DoubleAnalogWaveform)
    assert list(request.double_analog_waveform.y_data) == [0.0, 0.0, 0.0]


def test___python_int16_analog_waveform___populate_measurement___measurement_updated_correctly() -> None:
    wfm_obj = AnalogWaveform(3, np.int16)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.i16_analog_waveform, waveform_pb2.I16AnalogWaveform)
    assert list(request.i16_analog_waveform.y_data) == [0, 0, 0]


def test___python_float64_complex_waveform___populate_measurement___measurement_updated_correctly() -> None:
    wfm_obj = ComplexWaveform(2, np.complex128)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.double_complex_waveform, waveform_pb2.DoubleComplexWaveform)
    assert list(request.double_complex_waveform.y_data) == [0.0, 0.0, 0.0, 0.0]


def test___python_int16_complex_waveform___populate_measurement___measurement_updated_correctly() -> None:
    wfm_obj = ComplexWaveform(2, ComplexInt32DType)
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.i16_complex_waveform, waveform_pb2.I16ComplexWaveform)
    assert list(request.i16_complex_waveform.y_data) == [0, 0, 0, 0]


def test___python_bool_digital_waveform___populate_measurement___measurement_updated_correctly() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    wfm_obj = DigitalWaveform.from_lines(data, signal_count=3)

    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, wfm_obj)

    assert isinstance(request.digital_waveform, waveform_pb2.DigitalWaveform)
    assert request.digital_waveform.y_data == b"\x00\x01\x00\x01\x00\x01"
    assert request.digital_waveform.signal_count == 3


def test___python_uint8_digital_waveform___populate_measurement___measurement_updated_correctly() -> None:
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


# ========================================================
# Populate Measurement Batch
# ========================================================
def test___python_vector_object___populate_measurement_batch___condition_updated_correctly() -> None:
    vector_obj = Vector([1.0, 2.0, 3.0], "amps")
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.0, 2.0, 3.0]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"


# ========================================================
# Convert from protobuf
# ========================================================
def test___scalar_proto___convert_from_protobuf___valid_python_scalar() -> None:
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="amps")}
    pb_value = scalar_pb2.Scalar(attributes=attrs, double_value=1.0)
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, Scalar)
    assert result.value == 1.0
    assert result.units == "amps"


def test___vector_proto___convert_from_protobuf___valid_python_vector() -> None:
    attrs = {"NI_UnitDescription": attribute_value_pb2.AttributeValue(string_value="amps")}
    pb_value = vector_pb2.Vector(
        attributes=attrs,
        double_array=array_pb2.DoubleArray(values=[1.0, 2.0, 3.0]),
    )
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, Vector)
    assert list(result) == [1.0, 2.0, 3.0]
    assert result.units == "amps"


def test___double_analog_waveform_proto___convert_from_protobuf___valid_python_float64_analog_waveform() -> None:
    pb_value = waveform_pb2.DoubleAnalogWaveform(y_data=[0.0, 0.0, 0.0])
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, AnalogWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 3
    assert result.dtype == np.float64


def test___i16_analog_waveform_proto___convert_from_protobuf___valid_python_int16_analog_waveform() -> None:
    pb_value = waveform_pb2.I16AnalogWaveform(y_data=[0, 0, 0])
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, AnalogWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 3
    assert result.dtype == np.int16


def test___double_complex_waveform_proto___convert_from_protobuf___valid_python_float64_complex_waveform() -> (
    None
):
    pb_value = waveform_pb2.DoubleComplexWaveform(y_data=[0.0, 0.0, 0.0, 0.0])
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, ComplexWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 2
    assert result.dtype == np.complex128


def test___i16_complex_waveform_proto___convert_from_protobuf___valid_python_int16_complex_waveform() -> None:
    pb_value = waveform_pb2.I16ComplexWaveform(y_data=[0, 0, 0, 0])
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, ComplexWaveform)
    assert result.sample_count == result.capacity == len(result.raw_data) == 2
    assert result.dtype == ComplexInt32DType


def test___digital_waveform_proto___convert_from_protobuf___valid_python_bool_digital_waveform() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.bool)
    pb_value = waveform_pb2.DigitalWaveform(y_data=data.tobytes(), signal_count=3)
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, DigitalWaveform)
    assert np.array_equal(result.data, data)
    assert result.signal_count == 3


def test___digital_waveform_proto___convert_from_protobuf___valid_python_uint8_digital_waveform() -> None:
    data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.uint8)
    pb_value = waveform_pb2.DigitalWaveform(y_data=data.tobytes(), signal_count=3)
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, DigitalWaveform)
    assert np.array_equal(result.data, data)
    assert result.signal_count == 3


def test___double_spectrum_proto___convert_from_protobuf___valid_python_spectrum() -> None:
    pb_value = waveform_pb2.DoubleSpectrum(
        data=[1.0, 2.0, 3.0],
        start_frequency=100.0,
        frequency_increment=10.0,
    )
    packed_any = _pack_into_any(pb_value)

    result = convert_from_protobuf(packed_any)

    assert isinstance(result, Spectrum)
    assert list(result.data) == [1.0, 2.0, 3.0]
    assert result.start_frequency == 100.0
    assert result.frequency_increment == 10.0


# ========================================================
# Pack/Unpack Helpers
# ========================================================
def _pack_into_any(proto_value: Message) -> any_pb2.Any:
    as_any = any_pb2.Any()
    as_any.Pack(proto_value)
    return as_any
