"""Acceptance tests for V2 measurement vectors and batch creation."""

import hightime as ht
import numpy as np
from nitypes.vector import Vector
from nitypes.waveform import (
    AnalogWaveform,
    NoneScaleMode,
    SampleIntervalMode,
    Timing,
)
from utilities import DataStoreContext

from ni.datastore.data.v2 import DataStoreClient, Measurement
from tests.acceptance._utils import append_hashed_time
from tests.acceptance_v2._utils import create_step


def test___publish_batch_floats___read_measurement_value_returns_vector(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch floats")
    expected_vector = Vector(values=[1.0, 2.0, 3.0, 4.0])

    with DataStoreClient() as data_store_client:
        step = create_step(data_store_client, description)
        measurement = data_store_client.create_measurement(
            description, [1.0, 2.0, 3.0, 4.0], step.id
        )
        vector = data_store_client.read_measurement_value(measurement.id, Vector)

    assert vector == expected_vector


def test___publish_batch_vector___read_measurement_value_returns_vector(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch vector")
    expected_vector = Vector(values=[1, 2, 3], units="Volts")

    with DataStoreClient() as data_store_client:
        step = create_step(data_store_client, description)
        measurement = data_store_client.create_measurement(description, expected_vector, step.id)
        vector = data_store_client.read_measurement_value(measurement.id, Vector)

    assert vector == expected_vector


def test___publish_batch_double_analog_waveforms___reads_each_waveform(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch analog waveforms")
    expected_waveforms = [
        AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
            scale_mode=NoneScaleMode(),
            timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
        ),
        AnalogWaveform(
            sample_count=3,
            raw_data=np.array([4.0, 5.0, 6.0]),
            scale_mode=NoneScaleMode(),
            timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
        ),
    ]

    with DataStoreClient() as data_store_client:
        step = create_step(data_store_client, description)
        measurements = data_store_client.batch_create_measurements(
            [
                Measurement(name=description, value=waveform, step_id=step.id)
                for waveform in expected_waveforms
            ]
        )
        read_waveforms = [
            data_store_client.read_measurement_value(measurement.id, AnalogWaveform)
            for measurement in measurements
        ]

    assert len(measurements) == len(expected_waveforms)
    for read_waveform, expected_waveform in zip(read_waveforms, expected_waveforms):
        assert read_waveform == expected_waveform


def test___publish_batch_vectors___reads_each_vector(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 batch vectors")
    expected_vectors = [
        Vector(values=[1, 2, 3], units="Volts"),
        Vector(values=[4, 5, 6], units="Volts"),
    ]

    with DataStoreClient() as data_store_client:
        step = create_step(data_store_client, description)
        measurements = data_store_client.batch_create_measurements(
            [
                Measurement(name=description, value=vector, step_id=step.id)
                for vector in expected_vectors
            ]
        )
        read_vectors = [
            data_store_client.read_measurement_value(measurement.id, Vector)
            for measurement in measurements
        ]

    assert len(measurements) == len(expected_vectors)
    for read_vector, expected_vector in zip(read_vectors, expected_vectors):
        assert read_vector == expected_vector
