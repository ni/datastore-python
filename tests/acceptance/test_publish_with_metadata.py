"""Acceptance test that publishes then queries waveform data and metadata."""

import numpy as np
from ni.datastore.data import (
    DataStoreClient,
    Step,
    TestResult,
)
from ni.datastore.metadata import (
    MetadataStoreClient,
    Operator,
    SoftwareItem,
    TestStation,
    Uut,
    UutInstance,
)
from nitypes.waveform import AnalogWaveform


def test___waveform_with_metadata___publish___query_read_returns_correct_data() -> None:
    with MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        # Create UUT instance
        uut = Uut(model_name="NI-9205", family="Analog")
        uut_id = metadata_store_client.create_uut(uut)
        uut_instance = UutInstance(uut_id=uut_id, serial_number="A861-12345")
        uut_instance_id = metadata_store_client.create_uut_instance(uut_instance=uut_instance)

        # Create Operator metadata
        operator_name = "John Bowery"
        operator_role = "Test Operator II"
        operator = Operator(operator_name=operator_name, role=operator_role)
        operator_id = metadata_store_client.create_operator(operator)

        # Create TestStation metadata
        test_station = TestStation(test_station_name="TestStation_12")
        test_station_id = metadata_store_client.create_test_station(test_station)

        # Create SoftwareItem metadata
        software_item = SoftwareItem(product="Windows", version="10.0.19044")
        software_item_id = metadata_store_client.create_software_item(software_item)
        software_item_2 = SoftwareItem(product="Python", version="3.12")
        software_item_2_id = metadata_store_client.create_software_item(software_item_2)

        # Create TestResult metadata
        test_result_name = "sample test result"
        queried_test_result = TestResult(
            test_result_name=test_result_name,
            operator_id=operator_id,
            test_station_id=test_station_id,
            software_item_ids=[software_item_id, software_item_2_id],
            uut_instance_id=uut_instance_id,
        )
        test_result_id = data_store_client.create_test_result(queried_test_result)

        name = "data publish sample"
        # Create waveform data to publish
        expected_waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
        )

        # Publish the waveform data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name=name,
            value=expected_waveform,
            step_id=step_id,
        )

        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        queried_test_result = data_store_client.get_test_result(found_measurement.test_result_id)
        assert queried_test_result.test_result_name == test_result_name

        operator = metadata_store_client.get_operator(queried_test_result.operator_id)
        assert operator.operator_name == operator_name
        assert operator.role == operator_role

        waveform = data_store_client.read_data(found_measurement, expected_type=AnalogWaveform)
        assert waveform == expected_waveform
