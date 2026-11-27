"""Acceptance tests for publishing and reading V2 measurement values."""

import hightime as ht
import numpy as np
import pytest
from nitypes.scalar import Scalar
from nitypes.waveform import (
    AnalogWaveform,
    ComplexWaveform,
    DigitalWaveform,
    SampleIntervalMode,
    Spectrum,
    Timing,
)
from nitypes.xy_data import XYData
from utilities import DataStoreContext

from ni.datastore.data.v2 import DataStoreClient, JsonValue, MeasurementValue
from tests.acceptance._utils import append_hashed_time
from tests.acceptance_v2._utils import create_test_result_and_step


@pytest.mark.parametrize(
    ("value", "expected_value", "expected_type"),
    [
        pytest.param(123.45, Scalar(123.45), Scalar, id="float"),
        pytest.param(Scalar(25, "Volts"), Scalar(25, "Volts"), Scalar, id="scalar-with-units"),
        pytest.param(
            {"reading": 5.2, "passed": True},
            {"reading": 5.2, "passed": True},
            dict,
            id="json-mapping",
        ),
        pytest.param(
            JsonValue({"reading": 5.2}, attributes={"unit": "V"}),
            JsonValue({"reading": 5.2}, attributes={"unit": "V"}),
            JsonValue,
            id="json-value-with-attributes",
        ),
        pytest.param(
            XYData.from_arrays_1d(
                x_array=[1.0, 2.0],
                y_array=[3.0, 4.0],
                dtype=np.float64,
                x_units="Amps",
                y_units="Seconds",
            ),
            XYData.from_arrays_1d(
                x_array=[1.0, 2.0],
                y_array=[3.0, 4.0],
                dtype=np.float64,
                x_units="Amps",
                y_units="Seconds",
            ),
            XYData,
            id="xydata",
        ),
        pytest.param(
            Spectrum.from_array_1d(
                array=[1.0, 10.0, 100.0],
                dtype=np.float64,
                start_frequency=1.0,
                frequency_increment=1.0,
            ),
            Spectrum.from_array_1d(
                array=[1.0, 10.0, 100.0],
                dtype=np.float64,
                start_frequency=1.0,
                frequency_increment=1.0,
            ),
            Spectrum,
            id="float64-spectrum",
        ),
        pytest.param(
            Spectrum.from_array_1d(
                array=[1.0, 10.0, 100.0],
                dtype=np.float32,
                start_frequency=1.0,
                frequency_increment=1.0,
            ),
            Spectrum.from_array_1d(
                array=[1.0, 10.0, 100.0],
                dtype=np.float32,
                start_frequency=1.0,
                frequency_increment=1.0,
            ),
            Spectrum,
            id="float32-spectrum",
        ),
        pytest.param(
            AnalogWaveform(
                sample_count=3,
                raw_data=np.array([1.0, 2.0, 3.0]),
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            AnalogWaveform(
                sample_count=3,
                raw_data=np.array([1.0, 2.0, 3.0]),
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            AnalogWaveform,
            id="float64-analog-waveform",
        ),
        pytest.param(
            AnalogWaveform(
                sample_count=3,
                dtype=np.float32,
                raw_data=np.array([1.0, 2.0, 3.0], dtype=np.float32),
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            AnalogWaveform(
                sample_count=3,
                dtype=np.float32,
                raw_data=np.array([1.0, 2.0, 3.0], dtype=np.float32),
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            AnalogWaveform,
            id="float32-analog-waveform",
        ),
        pytest.param(
            DigitalWaveform(
                10,
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            DigitalWaveform(
                10,
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            DigitalWaveform,
            id="digital-waveform",
        ),
        pytest.param(
            ComplexWaveform(
                10,
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            ComplexWaveform(
                10,
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            ComplexWaveform,
            id="float64-complex-waveform",
        ),
        pytest.param(
            ComplexWaveform(
                10,
                dtype=np.complex64,
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            ComplexWaveform(
                10,
                dtype=np.complex64,
                timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
            ),
            ComplexWaveform,
            id="float32-complex-waveform",
        ),
    ],
)
def test___publish_measurement___read_measurement_value_returns_expected_type(
    acceptance_test_context: DataStoreContext,
    value: MeasurementValue,
    expected_value: object,
    expected_type: type[object],
) -> None:
    description = append_hashed_time("v2 measurement value")

    with DataStoreClient() as data_store_client:
        step = create_test_result_and_step(data_store_client, description)
        measurement = data_store_client.create_measurement(description, value, step.id)
        read_value = data_store_client.read_measurement_value(measurement.id)

    assert isinstance(read_value, expected_type)
    assert read_value == expected_value
