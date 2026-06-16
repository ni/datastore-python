from collections.abc import Generator
from typing import Any, Iterable

import numpy as np
import pytest
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)
from ni.protobuf.types import (
    scalar_pb2,
    vector_pb2,
    vector_wrappers_pb2,
    waveform_pb2,
    waveform_wrappers_pb2,
    xydata_pb2,
    xydata_wrappers_pb2,
)
from nitypes.complex import ComplexInt32DType
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData

from ni.datastore.data._grpc_conversion import (
    populate_publish_condition_batch_request_values,
    populate_publish_condition_request_value,
    populate_publish_measurement_batch_request_values,
    populate_publish_measurement_request_value,
)


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


def test___python_scalar_iterable___populate_condition_batch___condition_updated_correctly() -> (
    None
):
    request = PublishConditionBatchRequest()
    populate_publish_condition_batch_request_values(request, [1.5, 2.5, 3.5])

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.5, 2.5, 3.5]


def test___python_scalar_generator_iterable___populate_condition_batch___condition_updated_correctly() -> (
    None
):
    def _values() -> Iterable[float]:
        yield 1.5
        yield 2.5
        yield 3.5

    request = PublishConditionBatchRequest()
    populate_publish_condition_batch_request_values(request, _values())

    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(request.scalar_values.double_array.values) == [1.5, 2.5, 3.5]


def test___empty_iterable___populate_condition_batch___raises_error() -> None:
    request = PublishConditionBatchRequest()

    with pytest.raises(ValueError, match="Cannot publish an empty Iterable."):
        populate_publish_condition_batch_request_values(request, [])


def test___empty_generator___populate_condition_batch___raises_error() -> None:
    def _values() -> Generator[float, None, None]:
        yield from []

    request = PublishConditionBatchRequest()

    with pytest.raises(ValueError, match="Cannot publish an empty Iterable."):
        populate_publish_condition_batch_request_values(request, _values())


def test___python_unsupported_iterable___populate_condition_batch___raises_error() -> None:
    values = [object(), object()]
    request = PublishConditionBatchRequest()

    with pytest.raises(
        TypeError,
        match="Unsupported iterable.",
    ):
        populate_publish_condition_batch_request_values(request, values)


def test___python_non_iterable___populate_condition_batch___raises_error() -> None:
    values = 42
    request = PublishConditionBatchRequest()

    with pytest.raises(
        TypeError,
        match="Unsupported condition values type",
    ):
        populate_publish_condition_batch_request_values(request, values)


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


@pytest.mark.parametrize(
    "values, attribute_name",
    [
        ([1.5, 2.5, 3.5], "double_array"),
        ([1, 2, 3], "sint32_array"),
        ([True, False, True], "bool_array"),
        (["one", "two", "three"], "string_array"),
    ],
)
def test___python_scalar_iterable___populate_measurement___measurement_updated_correctly(
    values: list[object], attribute_name: str
) -> None:
    request = PublishMeasurementRequest()
    populate_publish_measurement_request_value(request, values)

    assert isinstance(request.vector, vector_pb2.Vector)
    assert list(getattr(request.vector, attribute_name).values) == values


def test___empty_iterable___populate_measurement___raises_value_error() -> None:
    request = PublishMeasurementRequest()
    with pytest.raises(ValueError, match="Cannot publish an empty Iterable."):
        populate_publish_measurement_request_value(request, [])


def test___unsupported_iterable___populate_measurement___raises_type_error() -> None:
    request = PublishMeasurementRequest()
    with pytest.raises(TypeError, match="Unsupported iterable"):
        populate_publish_measurement_request_value(request, [object(), object()])


# ========================================================
# Populate Measurement Batch
# ========================================================
def _assert_scalar_values(
    request: PublishMeasurementBatchRequest, attribute_name: str, expected_values: list[object]
) -> None:
    assert isinstance(request.scalar_values, vector_pb2.Vector)
    assert list(getattr(request.scalar_values, attribute_name).values) == expected_values


@pytest.mark.parametrize(
    "values, attribute_name, expected_unit",
    [
        (Vector([1.5, 2.5, 3.5], "amps"), "double_array", "amps"),
        (Vector([1, 2, 3], "volts"), "sint32_array", "volts"),
        (Vector([True, False, True], "state"), "bool_array", "state"),
        (Vector(["one", "two", "three"], "labels"), "string_array", "labels"),
    ],
)
def test___python_vector_object___populate_measurement_batch___measurement_updated_correctly(
    values: Vector[Any], attribute_name: str, expected_unit: str
) -> None:
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, values)

    _assert_scalar_values(request, attribute_name, list(values))
    assert request.scalar_values.attributes["NI_UnitDescription"].string_value == expected_unit


@pytest.mark.parametrize(
    "values, attribute_name",
    [
        ([1.5, 2.5, 3.5], "double_array"),
        ([1, 2, 3], "sint32_array"),
        ([True, False, True], "bool_array"),
        (["one", "two", "three"], "string_array"),
    ],
)
def test___python_scalar_iterable___populate_measurement_batch___measurement_updated_correctly(
    values: list[object], attribute_name: str
) -> None:
    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, values)

    _assert_scalar_values(request, attribute_name, values)


def test___python_vector_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [Vector([1.0, 2.0]), Vector([3.0, 4.0])]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(request.vector_values, vector_wrappers_pb2.VectorArrayValue)
    assert len(request.vector_values.vectors) == 2
    assert list(request.vector_values.vectors[0].double_array.values) == [1.0, 2.0]
    assert list(request.vector_values.vectors[1].double_array.values) == [3.0, 4.0]


def test___python_float64_analog_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64)),
        AnalogWaveform(sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float64)),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(
        request.double_analog_waveform_values, waveform_wrappers_pb2.DoubleAnalogWaveformArrayValue
    )
    assert len(request.double_analog_waveform_values.waveforms) == 2
    assert list(request.double_analog_waveform_values.waveforms[0].y_data) == [1.25, -2.5]
    assert list(request.double_analog_waveform_values.waveforms[1].y_data) == [3.5, 4.75, -6.0]


def test___python_int16_analog_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        AnalogWaveform(sample_count=2, raw_data=np.array([12, -3], dtype=np.int16)),
        AnalogWaveform(sample_count=3, raw_data=np.array([7, 0, -8], dtype=np.int16)),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(
        request.i16_analog_waveform_values, waveform_wrappers_pb2.I16AnalogWaveformArrayValue
    )
    assert len(request.i16_analog_waveform_values.waveforms) == 2
    assert list(request.i16_analog_waveform_values.waveforms[0].y_data) == [12, -3]
    assert list(request.i16_analog_waveform_values.waveforms[1].y_data) == [7, 0, -8]


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

    assert isinstance(
        request.double_complex_waveform_values,
        waveform_wrappers_pb2.DoubleComplexWaveformArrayValue,
    )
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

    assert isinstance(
        request.i16_complex_waveform_values, waveform_wrappers_pb2.I16ComplexWaveformArrayValue
    )
    assert len(request.i16_complex_waveform_values.waveforms) == 2
    assert list(request.i16_complex_waveform_values.waveforms[0].y_data) == [11, -2, 5, 9]
    assert list(request.i16_complex_waveform_values.waveforms[1].y_data) == [-7, 4, 0, -6, 8, 3]


def test___python_float64_spectrum_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        Spectrum.from_array_1d(np.array([1.0, 2.0])),
        Spectrum.from_array_1d(np.array([3.0, 4.0])),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(
        request.double_spectrum_values, waveform_wrappers_pb2.DoubleSpectrumArrayValue
    )
    assert len(request.double_spectrum_values.waveforms) == 2
    assert list(request.double_spectrum_values.waveforms[0].data) == [1.0, 2.0]
    assert list(request.double_spectrum_values.waveforms[1].data) == [3.0, 4.0]


def test___python_uint8_digital_waveform_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        DigitalWaveform.from_lines([1], np.uint8),
        DigitalWaveform.from_lines([0], np.uint8),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(
        request.digital_waveform_values, waveform_wrappers_pb2.DigitalWaveformArrayValue
    )
    assert len(request.digital_waveform_values.waveforms) == 2
    assert request.digital_waveform_values.waveforms[0].y_data == b"\x01"
    assert request.digital_waveform_values.waveforms[1].y_data == b"\x00"


def test___python_float64_xydata_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    values = [
        XYData.from_arrays_1d([1.0], [2.0], np.float64),
        XYData.from_arrays_1d([3.0], [4.0], np.float64),
    ]
    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, values)

    assert isinstance(request.x_y_data_values, xydata_wrappers_pb2.DoubleXYDataArrayValue)
    assert len(request.x_y_data_values.x_y_data) == 2
    assert list(request.x_y_data_values.x_y_data[0].x_data) == [1.0]
    assert list(request.x_y_data_values.x_y_data[0].y_data) == [2.0]
    assert list(request.x_y_data_values.x_y_data[1].x_data) == [3.0]
    assert list(request.x_y_data_values.x_y_data[1].y_data) == [4.0]


def test___python_scalar_generator_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    def _values() -> Iterable[float]:
        yield 1.5
        yield 2.5
        yield 3.5

    request = PublishMeasurementBatchRequest()
    populate_publish_measurement_batch_request_values(request, _values())

    _assert_scalar_values(request, "double_array", [1.5, 2.5, 3.5])


def test___python_non_scalar_generator_iterable___populate_measurement_batch___measurement_updated_correctly() -> (
    None
):
    def _values() -> Iterable[AnalogWaveform[np.float64]]:
        yield AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64))
        yield AnalogWaveform(sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float64))

    request = PublishMeasurementBatchRequest()

    populate_publish_measurement_batch_request_values(request, _values())

    assert isinstance(
        request.double_analog_waveform_values, waveform_wrappers_pb2.DoubleAnalogWaveformArrayValue
    )
    assert len(request.double_analog_waveform_values.waveforms) == 2
    assert list(request.double_analog_waveform_values.waveforms[0].y_data) == [1.25, -2.5]
    assert list(request.double_analog_waveform_values.waveforms[1].y_data) == [3.5, 4.75, -6.0]


@pytest.mark.parametrize(
    "values, error_message",
    [
        pytest.param(
            [
                Vector([1.0, 2.0]),
                AnalogWaveform(sample_count=2, raw_data=np.array([1.0, 2.0])),
            ],
            "Unsupported iterable: all values must be Vector.",
            id="vector",
        ),
        pytest.param(
            [
                AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64)),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be float64 AnalogWaveform.",
            id="float64_analog_waveform",
        ),
        pytest.param(
            [
                AnalogWaveform(sample_count=2, raw_data=np.array([12, -3], dtype=np.int16)),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be int16 AnalogWaveform.",
            id="int16_analog_waveform",
        ),
        pytest.param(
            [
                ComplexWaveform(
                    sample_count=2,
                    raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex128),
                ),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be complex128 ComplexWaveform.",
            id="float64_complex_waveform",
        ),
        pytest.param(
            [
                ComplexWaveform(
                    sample_count=2,
                    raw_data=np.array([(11, -2), (5, 9)], dtype=ComplexInt32DType),
                ),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be ComplexWaveform with ComplexInt32DType.",
            id="int16_complex_waveform",
        ),
        pytest.param(
            [
                Spectrum.from_array_1d(np.array([1.0, 2.0])),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be float64 Spectrum.",
            id="spectrum",
        ),
        pytest.param(
            [
                DigitalWaveform.from_lines([1], np.uint8),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be DigitalWaveform.",
            id="digital_waveform",
        ),
        pytest.param(
            [
                XYData.from_arrays_1d([1.0], [2.0], np.float64),
                Vector([1.0, 2.0]),
            ],
            "Unsupported iterable: all values must be float64 XYData.",
            id="xydata",
        ),
    ],
)
def test___python_iterable_with_mismatched_second_element___populate_measurement_batch___raises_error(
    values: list[object], error_message: str
) -> None:
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match=error_message):
        populate_publish_measurement_batch_request_values(request, values)


@pytest.mark.parametrize(
    "values, error_message",
    [
        pytest.param(
            [
                AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float64)),
                AnalogWaveform(sample_count=3, raw_data=np.array([7, 0, -8], dtype=np.int16)),
            ],
            "Unsupported iterable: all values must be float64 AnalogWaveform.",
            id="float64_analog_waveform",
        ),
        pytest.param(
            [
                AnalogWaveform(sample_count=2, raw_data=np.array([12, -3], dtype=np.int16)),
                AnalogWaveform(
                    sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float64)
                ),
            ],
            "Unsupported iterable: all values must be int16 AnalogWaveform.",
            id="int16_analog_waveform",
        ),
        pytest.param(
            [
                ComplexWaveform(
                    sample_count=2,
                    raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex128),
                ),
                ComplexWaveform(
                    sample_count=3,
                    raw_data=np.array([(-7, 4), (0, -6), (8, 3)], dtype=ComplexInt32DType),
                ),
            ],
            "Unsupported iterable: all values must be complex128 ComplexWaveform.",
            id="float64_complex_waveform",
        ),
        pytest.param(
            [
                ComplexWaveform(
                    sample_count=2,
                    raw_data=np.array([(11, -2), (5, 9)], dtype=ComplexInt32DType),
                ),
                ComplexWaveform(
                    sample_count=3,
                    raw_data=np.array([0.5 - 1.5j, 2.25 + 0.75j, -4.0 - 2.0j], dtype=np.complex128),
                ),
            ],
            "Unsupported iterable: all values must be ComplexWaveform with ComplexInt32DType.",
            id="int16_complex_waveform",
        ),
        pytest.param(
            [
                Spectrum.from_array_1d(np.array([1.0, 2.0])),
                Spectrum.from_array_1d(np.array([3.0, 4.0], dtype=np.float32)),
            ],
            "Unsupported iterable: all values must be float64 Spectrum.",
            id="spectrum",
        ),
        pytest.param(
            [
                XYData.from_arrays_1d([1.0], [2.0], np.float64),
                XYData.from_arrays_1d([3.0], [4.0], np.float32),
            ],
            "Unsupported iterable: all values must be float64 XYData.",
            id="xydata",
        ),
    ],
)
def test___python_iterable_with_mismatched_second_dtype___populate_measurement_batch___raises_error(
    values: list[object], error_message: str
) -> None:
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match=error_message):
        populate_publish_measurement_batch_request_values(request, values)


@pytest.mark.parametrize(
    "values, error_message",
    [
        pytest.param(
            [
                AnalogWaveform(sample_count=2, raw_data=np.array([1.25, -2.5], dtype=np.float32)),
                AnalogWaveform(
                    sample_count=3, raw_data=np.array([3.5, 4.75, -6.0], dtype=np.float32)
                ),
            ],
            "Unsupported AnalogWaveform dtype",
            id="analog_waveform",
        ),
        pytest.param(
            [
                ComplexWaveform(
                    sample_count=2,
                    raw_data=np.array([1.0 + 2.0j, -3.0 + 4.5j], dtype=np.complex64),
                ),
                ComplexWaveform(
                    sample_count=3,
                    raw_data=np.array([0.5 - 1.5j, 2.25 + 0.75j, -4.0 - 2.0j], dtype=np.complex64),
                ),
            ],
            "Unsupported ComplexWaveform dtype",
            id="complex_waveform",
        ),
        pytest.param(
            [
                Spectrum.from_array_1d(np.array([1.0, 2.0], dtype=np.float32)),
                Spectrum.from_array_1d(np.array([3.0, 4.0], dtype=np.float32)),
            ],
            "Unsupported Spectrum dtype",
            id="spectrum",
        ),
        pytest.param(
            [
                XYData.from_arrays_1d([1.0], [2.0], np.float32),
                XYData.from_arrays_1d([3.0], [4.0], np.float32),
            ],
            "Unsupported XYData dtype",
            id="xydata",
        ),
    ],
)
def test___python_unsupported_dtype_iterable___populate_measurement_batch___raises_error(
    values: list[object], error_message: str
) -> None:
    request = PublishMeasurementBatchRequest()

    with pytest.raises(TypeError, match=error_message):
        populate_publish_measurement_batch_request_values(request, values)


def test___empty_iterable___populate_measurement_batch___raises_error() -> None:
    request = PublishMeasurementBatchRequest()

    with pytest.raises(ValueError, match="Cannot publish an empty Iterable."):
        populate_publish_measurement_batch_request_values(request, [])


def test___empty_generator___populate_measurement_batch___raises_error() -> None:
    def _values() -> Generator[float, None, None]:
        yield from []

    request = PublishMeasurementBatchRequest()

    with pytest.raises(ValueError, match="Cannot publish an empty Iterable."):
        populate_publish_measurement_batch_request_values(request, _values())


def test___python_unsupported_iterable___populate_measurement_batch___raises_error() -> None:
    values = [object(), object()]
    request = PublishMeasurementBatchRequest()

    with pytest.raises(
        TypeError,
        match="Unsupported iterable. Subtype must be",
    ):
        populate_publish_measurement_batch_request_values(request, values)


def test___python_non_iterable___populate_measurement_batch___raises_error() -> None:
    values = 42
    request = PublishMeasurementBatchRequest()

    with pytest.raises(
        TypeError,
        match="Unsupported measurement values type",
    ):
        populate_publish_measurement_batch_request_values(request, values)
