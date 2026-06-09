"""Acceptance tests that publish various batch measurement values then reads the data back."""

import numpy as np
import hightime as ht
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, NoneScaleMode, Timing, SampleIntervalMode
from utilities import DataStoreContext

from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)


def test___publish_batch_floats___read_measurement_value_returns_vector(
    acceptance_test_context: DataStoreContext,
) -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish batch floats acceptance test"
        test_result = TestResult(name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Publish the waveform data
        step = Step(name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement_ids = data_store_client.publish_measurement_batch(
            name="Test measurement",
            values=[1.0, 2.0, 3.0, 4.0],
            step_id=step_id,
        )
        published_measurement_id = next(iter(published_measurement_ids), None)
        assert published_measurement_id is not None and published_measurement_id != ""

        # Get the published measurement object to read data from it
        published_measurement = data_store_client.get_measurement(published_measurement_id)

        # A published batch floats will be read back as a Vector.
        vector = data_store_client.read_measurement_value(
            published_measurement, expected_type=Vector
        )
        assert vector._values == [1.0, 2.0, 3.0, 4.0]
        assert vector.units == ""


def test___publish_batch_vector___read_measurement_value_returns_vector(
    acceptance_test_context: DataStoreContext,
) -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish batch Vector acceptance test"
        test_result = TestResult(name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create a Vector data to publish
        expected_vector = Vector(values=[1, 2, 3], units="Volts")

        # Batch publish the vector
        step = Step(name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement_ids = data_store_client.publish_measurement_batch(
            name="Test measurement",
            values=expected_vector,
            step_id=step_id,
        )
        published_measurement_id = next(iter(published_measurement_ids), None)
        assert published_measurement_id is not None and published_measurement_id != ""

        # Get the published measurement object to read data from it
        published_measurement = data_store_client.get_measurement(published_measurement_id)

        # A batch published Vector will be read back as a Vector.
        vector = data_store_client.read_measurement_value(
            published_measurement, expected_type=Vector
        )
        assert vector == expected_vector


def test___publish_batch_double_analog_waveforms___read_measurement_value_returns_each_analog_waveform(
    acceptance_test_context: DataStoreContext,
) -> None:
    with DataStoreClient() as data_store_client:
        test_result_name = "python publish batch AnalogWaveforms acceptance test"
        test_result = TestResult(name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)
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
        step = Step(name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)

        published_measurement_ids = data_store_client.publish_measurement_batch(
            name="Test measurement",
            values=expected_waveforms,
            step_id=step_id,
        )

        assert len(published_measurement_ids) == 2
        published_measurement_one = data_store_client.get_measurement(published_measurement_ids[0])
        published_measurement_two = data_store_client.get_measurement(published_measurement_ids[1])
        published_waveform_one = data_store_client.read_measurement_value(
            published_measurement_one, expected_type=AnalogWaveform
        )
        published_waveform_two = data_store_client.read_measurement_value(
            published_measurement_two, expected_type=AnalogWaveform
        )
        assert published_waveform_one == expected_waveforms[0]
        assert published_waveform_two == expected_waveforms[1]


def test___publish_batch_vectors___read_measurement_value_returns_each_vector(
    acceptance_test_context: DataStoreContext,
) -> None:
    with DataStoreClient() as data_store_client:
        test_result_name = "python publish batch Vectors acceptance test"
        test_result = TestResult(name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)
        expected_vectors = [
            Vector(values=[1, 2, 3], units="Volts"),
            Vector(values=[4, 5, 6], units="Volts"),
        ]
        step = Step(name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)

        published_measurement_ids = data_store_client.publish_measurement_batch(
            name="Test measurement",
            values=expected_vectors,
            step_id=step_id,
        )

        assert len(published_measurement_ids) == 2
        published_measurement_one = data_store_client.get_measurement(published_measurement_ids[0])
        published_measurement_two = data_store_client.get_measurement(published_measurement_ids[1])
        published_vector_one = data_store_client.read_measurement_value(
            published_measurement_one, expected_type=Vector
        )
        published_vector_two = data_store_client.read_measurement_value(
            published_measurement_two, expected_type=Vector
        )
        assert published_vector_one == expected_vectors[0]
        assert published_vector_two == expected_vectors[1]
