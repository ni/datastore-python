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
def test___python_vector_object___populate_condition_batch___condition_updated_correctly() -> None:
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
def test___python_double_vector_object___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    vector_obj = Vector([1.5, 2.5, 3.5], "amps")
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.5, 2.5, 3.5]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_int_vector_object___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    vector_obj = Vector([1, 2, 3], "amps")
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.sint32_array.values) == [1, 2, 3]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_bool_vector_object___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    vector_obj = Vector([True, False, True], "amps")
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.bool_array.values) == [True, False, True]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_string_vector_object___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    vector_obj = Vector(["one", "two", "three"], "amps")
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, vector_obj)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == "amps"


def test___python_double_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [1.5, 2.5, 3.5]
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.5, 2.5, 3.5]


def test___python_int_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [1, 2, 3]
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.sint32_array.values) == [1, 2, 3]


def test___python_bool_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [True, False, True]
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.bool_array.values) == [True, False, True]


def test___python_string_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = ["one", "two", "three"]
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.string_array.values) == ["one", "two", "three"]


def test___python_vector_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [Vector([1.0, 2.0]), Vector([3.0, 4.0])]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.vector_values.vectors) == 2
    assert list(request.vector_values.vectors[0].double_array.values) == [1.0, 2.0]
    assert list(request.vector_values.vectors[1].double_array.values) == [3.0, 4.0]


def test___python_vector_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [Vector([1.0, 2.0]), AnalogWaveform(sample_count=2, raw_data=np.array([1.0, 2.0]))]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_analog_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64)),
        AnalogWaveform(sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float64)),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.double_analog_waveform_values.waveforms) == 2
    assert list(request.double_analog_waveform_values.waveforms[0].y_data) == [1.25, -2.5]
    assert list(request.double_analog_waveform_values.waveforms[1].y_data) == [3.5, 4.75, -6.0]


def test___python_float64_analog_waveform_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64)),
        Vector([3.5, 4.75, -6.0]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_analog_waveform_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64)),
        AnalogWaveform(sample_count=3, raw_data=np.array([7, 0, -8], dtype=np.int16)),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_int16_analog_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([12, -3], dtype=np.int16)),
        AnalogWaveform(sample_count=3, raw_data=np.array([7, 0, -8], dtype=np.int16)),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.i16_analog_waveform_values.waveforms) == 2
    assert list(request.i16_analog_waveform_values.waveforms[0].y_data) == [12, -3]
    assert list(request.i16_analog_waveform_values.waveforms[1].y_data) == [7, 0, -8]


def test___python_int16_analog_waveform_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([12, -3], dtype=np.int16)),
        Vector([7.0, 0.0, -8.0]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_int16_analog_waveform_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([12, -3], dtype=np.int16)),
        AnalogWaveform(sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float64)),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_unsupported_dtype_analog_waveform_iterable___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float32)),
        AnalogWaveform(sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float32)),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported AnalogWaveform dtype"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_complex_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2, raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex128)
        ),
        ComplexWaveform(
            sample_count=3,
            raw_data=np.array([0.5 - 1.5j, 2.25 + 0.75j, -4.0 - 2.0j], dtype=np.complex128),
        ),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.double_complex_waveform_values.waveforms) == 2
    assert list(request.double_complex_waveform_values.waveforms[0].y_data) == [1.0, 2.0, -3.0, 4.5]
    assert list(request.double_complex_waveform_values.waveforms[1].y_data) == [
        0.5,
        -1.5,
        2.25,
        0.75,
        -4.0,
        -2.0,
    ]


def test___python_float64_complex_waveform_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2, raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex128)
        ),
        Vector([0.5, -1.5, 2.25, 0.75]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_complex_waveform_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2, raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex128)
        ),
        ComplexWaveform(
            sample_count=3,
            raw_data=np.array([(-7, 4), (0, -6), (8, 3)], dtype=ComplexInt32DType),
        ),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_int16_complex_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2,
            raw_data=np.array([(11, -2), (5, 9)], dtype=ComplexInt32DType),
        ),
        ComplexWaveform(
            sample_count=3,
            raw_data=np.array([(-7, 4), (0, -6), (8, 3)], dtype=ComplexInt32DType),
        ),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.i16_complex_waveform_values.waveforms) == 2
    assert list(request.i16_complex_waveform_values.waveforms[0].y_data) == [11, -2, 5, 9]
    assert list(request.i16_complex_waveform_values.waveforms[1].y_data) == [-7, 4, 0, -6, 8, 3]


def test___python_int16_complex_waveform_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2,
            raw_data=np.array([(11, -2), (5, 9)], dtype=ComplexInt32DType),
        ),
        Vector([-7.0, 4.0, 0.0, -6.0]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_int16_complex_waveform_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2,
            raw_data=np.array([(11, -2), (5, 9)], dtype=ComplexInt32DType),
        ),
        ComplexWaveform(
            sample_count=3,
            raw_data=np.array([0.5 - 1.5j, 2.25 + 0.75j, -4.0 - 2.0j], dtype=np.complex128),
        ),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_unsupported_dtype_complex_waveform_iterable___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        ComplexWaveform(
            sample_count=2, raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex64)
        ),
        ComplexWaveform(
            sample_count=3,
            raw_data=np.array([0.5 - 1.5j, 2.25 + 0.75j, -4.0 - 2.0j], dtype=np.complex64),
        ),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported ComplexWaveform dtype"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_spectrum_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        Spectrum.from_array_1d(np.array([1.0, 2.0])),
        Spectrum.from_array_1d(np.array([3.0, 4.0])),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.double_spectrum_values.waveforms) == 2
    assert list(request.double_spectrum_values.waveforms[0].data) == [1.0, 2.0]
    assert list(request.double_spectrum_values.waveforms[1].data) == [3.0, 4.0]


def test___python_float64_spectrum_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        Spectrum.from_array_1d(np.array([1.0, 2.0])),
        Vector([3.0, 4.0]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_spectrum_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        Spectrum.from_array_1d(np.array([1.0, 2.0])),
        Spectrum.from_array_1d(np.array([3.0, 4.0], dtype=np.float32)),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_unsupported_dtype_spectrum_iterable___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        Spectrum.from_array_1d(np.array([1.0, 2.0], dtype=np.float32)),
        Spectrum.from_array_1d(np.array([3.0, 4.0], dtype=np.float32)),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported Spectrum dtype"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_uint8_digital_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        DigitalWaveform.from_lines([1], np.uint8),
        DigitalWaveform.from_lines([0], np.uint8),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.digital_waveform_values.waveforms) == 2
    assert request.digital_waveform_values.waveforms[0].y_data == b"\x01"
    assert request.digital_waveform_values.waveforms[1].y_data == b"\x00"


def test___python_uint8_digital_waveform_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        DigitalWaveform.from_lines([1], np.uint8),
        Vector([0.0]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_xydata_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        XYData.from_arrays_1d([1.0], [2.0], np.float64),
        XYData.from_arrays_1d([3.0], [4.0], np.float64),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert len(request.x_y_data_values.x_y_data) == 2
    assert list(request.x_y_data_values.x_y_data[0].x_data) == [1.0]
    assert list(request.x_y_data_values.x_y_data[0].y_data) == [2.0]
    assert list(request.x_y_data_values.x_y_data[1].x_data) == [3.0]
    assert list(request.x_y_data_values.x_y_data[1].y_data) == [4.0]


def test___python_float64_xydata_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        XYData.from_arrays_1d([1.0], [2.0], np.float64),
        Vector([3.0, 4.0]),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_float64_xydata_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        XYData.from_arrays_1d([1.0], [2.0], np.float64),
        XYData.from_arrays_1d([3.0], [4.0], np.float32),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_unsupported_dtype_xydata_iterable___populate_measurement_batch___raises_error() -> (
    None
):
    values = [
        XYData.from_arrays_1d([1.0], [2.0], np.float32),
        XYData.from_arrays_1d([3.0], [4.0], np.float32),
    ]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match="Unsupported XYData dtype"):
        populate_publish_measurement_batch_request_values(request, values)


def test___empty_iterable___populate_measurement_batch___raises_error() -> None:
    request = PublishMeasurementBatchRequest()

    with pytest.raises(ValueError, match="Cannot publish an empty Iterable\."):
        populate_publish_measurement_batch_request_values(request, [])


def test___python_unsupported_iterable___populate_measurement_batch___raises_error() -> None:
    values = [object(), object()]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(
        TypeError,
        match="Unsupported iterable\. Subtype must be",
    ):
        populate_publish_measurement_batch_request_values(request, values)
