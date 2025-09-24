"""Overview example demonstrating data publishing and querying."""

from datetime import datetime, timedelta, timezone

import numpy as np
from ni.datastore.client import Client
from ni.measurements.data.v1.data_store_pb2 import Step, TestResult
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Operator,
    SoftwareItem,
    TestStation,
    Uut,
    UutInstance,
)
from nitypes.waveform import AnalogWaveform, Timing


def main() -> None:
    published_measurement_id = publish_data()
    query_data(published_measurement_id)

def publish_data() -> str:
    """Demonstrate data publishing of an AnalogWaveform."""
    client = Client()

    # Create UUT instance
    uut = Uut(model_name="NI-6508", family="Digital")
    uut_id = client.create_uut(uut)
    uut_instance = UutInstance(uut_id=uut_id, serial_number="A861-42367")
    uut_instance_id = client.create_uut_instance(uut_instance=uut_instance)

    # Create Operator metadata
    operator = Operator(operator_name="James Bowery", role="Test Operator")
    operator_id = client.create_operator(operator)
    print(f"created operator_id: {operator_id}")

    # Create TestStation metadata
    test_station = TestStation(test_station_name="TestStation_12")
    test_station_id = client.create_test_station(test_station)
    print(f"created test_station_id: {test_station_id}")

    # Create SoftwareItem metadata
    software_item = SoftwareItem(product="Windows", version="10.0.19044")
    software_item_id = client.create_software_item(software_item)
    print(f"created software_item_id: {software_item_id}")
    software_item_2 = SoftwareItem(product="Python", version="3.12")
    software_item_2_id = client.create_software_item(software_item_2)
    print(f"created software_item_2_id: {software_item_2_id}")

    # Create TestResult metadata
    test_result = TestResult(
        test_result_name="sample test result",
        operator_id=operator_id,
        test_station_id=test_station_id,
        software_item_ids=[software_item_id, software_item_2_id],
        uut_instance_id=uut_instance_id,
    )
    test_result_id = client.create_test_result(test_result)
    print(f"created test_result_id: {test_result_id}")

    name = "data publish sample"
    # Create waveform data to publish
    waveform = AnalogWaveform(
        sample_count=3,
        raw_data=np.array([1.0, 2.0, 3.0]),
        timing=Timing.create_with_regular_interval(
            timedelta(seconds=1e-3), datetime.now(timezone.utc)
        ),
    )

    # Publish the test step with the waveform data
    step = Step(step_name="Initial step", test_result_id=test_result_id)
    step_id = client.create_step(step)
    published_measurement = client.publish_measurement(
        measurement_name=name,
        value=waveform,
        step_id=step_id,
    )
    print(
        f"Published measurement: '{published_measurement.measurement_name}' with id {published_measurement.published_measurement_id}"
    )
    return published_measurement.published_measurement_id

def query_data(published_measurement_id: str) -> None:
    """Demonstrate data publishing of an AnalogWaveform."""
    client = Client()
    published_measurements = client.query_measurements(
        odata_query=f"$filter=id eq {published_measurement_id}"
    )
    found_measurement = next(iter(published_measurements), None)

    if found_measurement is not None:
        print(
            f"Found published measurement: '{found_measurement.measurement_name}' with id {found_measurement.published_measurement_id}"
        )
        test_result = client.get_test_result(found_measurement.test_result_id)
        operator = client.get_operator(test_result.operator_id)

        waveform = client.read_data(found_measurement.moniker, expected_type=AnalogWaveform)
        print(f"published data is: {waveform.raw_data}")


if __name__ == "__main__":
    main()
