"""Overview example demonstrating data publishing and querying."""

from datetime import timezone

import hightime as ht
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
from nitypes.waveform import AnalogWaveform, Timing


def main() -> None:
    """Main function to demonstrate data publishing and querying."""
    published_measurement_id = publish_data()
    query_data(published_measurement_id)


def publish_data() -> str:
    """Demonstrate data publishing of an AnalogWaveform."""
    with MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        # Create UUT instance
        uut = Uut(model_name="NI-6508", family="Digital")
        uut_id = metadata_store_client.create_uut(uut)
        uut_instance = UutInstance(uut_id=uut_id, serial_number="A861-42367")
        uut_instance_id = metadata_store_client.create_uut_instance(uut_instance=uut_instance)

        # Create Operator metadata
        operator = Operator(operator_name="James Bowery", role="Test Operator")
        operator_id = metadata_store_client.create_operator(operator)
        print(f"created operator_id: {operator_id}")

        # Create TestStation metadata
        test_station = TestStation(test_station_name="TestStation_12")
        test_station_id = metadata_store_client.create_test_station(test_station)
        print(f"created test_station_id: {test_station_id}")

        # Create SoftwareItem metadata
        software_item = SoftwareItem(product="Windows", version="10.0.19044")
        software_item_id = metadata_store_client.create_software_item(software_item)
        print(f"created software_item_id: {software_item_id}")
        software_item_2 = SoftwareItem(product="Python", version="3.12")
        software_item_2_id = metadata_store_client.create_software_item(software_item_2)
        print(f"created software_item_2_id: {software_item_2_id}")

        # Create TestResult metadata
        test_result = TestResult(
            test_result_name="sample test result",
            operator_id=operator_id,
            test_station_id=test_station_id,
            software_item_ids=[software_item_id, software_item_2_id],
            uut_instance_id=uut_instance_id,
        )
        test_result_id = data_store_client.create_test_result(test_result)
        print(f"created test_result_id: {test_result_id}")

        name = "data publish sample"
        # Create waveform data to publish
        waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
            timing=Timing.create_with_regular_interval(
                ht.timedelta(seconds=1e-3), ht.datetime.now(timezone.utc)
            ),
        )

        # Publish the test step with the waveform data
        step = Step(step_name="Initial step", test_result_id=test_result_id)
        step_id = data_store_client.create_step(step)
        published_measurement = data_store_client.publish_measurement(
            measurement_name=name,
            value=waveform,
            step_id=step_id,
        )
        print(
            f"Published measurement: '{published_measurement.measurement_name}' with id {published_measurement.id}"
        )

    return published_measurement.id


def query_data(published_measurement_id: str) -> None:
    """Demonstrate querying a published AnalogWaveform measurement."""
    with MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)

        if found_measurement is not None:
            print(
                f"Found published measurement: '{found_measurement.measurement_name}' with id {found_measurement.id}"
            )
            test_result = data_store_client.get_test_result(found_measurement.test_result_id)
            print(f"test_result: {test_result.test_result_name}")
            operator = metadata_store_client.get_operator(test_result.operator_id)
            print(f"operator: {operator}")

            waveform = data_store_client.read_data(found_measurement, expected_type=AnalogWaveform)
            print(f"published data is: {waveform.raw_data}")


if __name__ == "__main__":
    main()
