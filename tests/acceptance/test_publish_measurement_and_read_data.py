"""Acceptance tests that publish various values then reads the data back."""

import numpy as np
from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum
from nitypes.xy_data import XYData


def test___publish_float___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish float acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Publish the waveform data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish float",
            value=123.45,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published integer will be read back as a Vector.
        vector = data_store_client.read_data(found_measurement, expected_type=Vector)
        assert vector[0] == 123.45
        assert vector.units == ""


def test___publish_scalar___read_data_returns_vector() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish scalar acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create scalar data to publish
        expected_scalar = Scalar(value=25, units="Volts")

        # Publish the waveform data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish scalar",
            value=expected_scalar,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published Scalar will be read back as a Vector.
        vector = data_store_client.read_data(found_measurement, expected_type=Vector)
        assert vector[0] == expected_scalar.value
        assert vector.units == expected_scalar.units


def test___publish_xydata___read_data_returns_xydata() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish xydata acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create scalar data to publish
        expected_xydata = XYData.from_arrays_1d(
            x_array=[1.0, 2.0],
            y_array=[3.0, 4.0],
            dtype=np.float64,
            x_units="Amps",
            y_units="Seconds",
        )

        # Publish the waveform data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish xydata",
            value=expected_xydata,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published Scalar will be read back as a Vector.
        xydata = data_store_client.read_data(found_measurement, expected_type=XYData)
        assert xydata == expected_xydata


def test___publish_spectrum___read_data_returns_spectrum() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish spectrum acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create spectrum data to publish
        expected_spectrum = Spectrum.from_array_1d(
            array=[1.0, 10.0, 100.0],
            dtype=np.float64,
            start_frequency=1.0,
            frequency_increment=1.0,
        )

        # Publish the spectrum data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish spectrum",
            value=expected_spectrum,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published Spectrum will be read back as a Spectrum.
        spectrum = data_store_client.read_data(found_measurement, expected_type=Spectrum)
        assert spectrum == expected_spectrum


def test___publish_analog_waveform___read_data_returns_analog_waveform() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish analog waveform acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create spectrum data to publish
        expected_waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
        )

        # Publish the spectrum data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish analog waveform",
            value=expected_waveform,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published AnalogWaveform will be read back as an AnalogWaveform.
        waveform = data_store_client.read_data(found_measurement, expected_type=AnalogWaveform)
        assert waveform == expected_waveform


def test___publish_digital_waveform___read_data_returns_digital_waveform() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish digital waveform acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create spectrum data to publish
        expected_waveform = DigitalWaveform(10)

        # Publish the spectrum data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish digital waveform",
            value=expected_waveform,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published DigitalWaveform will be read back as an DigitalWaveform.
        waveform = data_store_client.read_data(found_measurement, expected_type=DigitalWaveform)
        assert waveform == expected_waveform


def test___publish_complex_waveform___read_data_returns_complex_waveform() -> None:
    with DataStoreClient() as data_store_client:
        # Create TestResult metadata
        test_result_name = "python publish complex waveform acceptance test"
        test_result = TestResult(test_result_name=test_result_name)
        test_result_id = data_store_client.create_test_result(test_result)

        # Create spectrum data to publish
        expected_waveform = ComplexWaveform(10)

        # Publish the spectrum data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name="python publish complex waveform",
            value=expected_waveform,
            step_id=step_id,
        )

        # Query for the measurement id and read/validate data
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # A published ComplexWaveform will be read back as an ComplexWaveform.
        waveform = data_store_client.read_data(found_measurement, expected_type=ComplexWaveform)
        assert waveform == expected_waveform
