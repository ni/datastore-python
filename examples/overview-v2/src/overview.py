"""Overview example demonstrating V2 data publishing and querying."""

import argparse
from datetime import timezone

import grpc
import hightime as ht
import numpy as np
from ni.datastore.data.v2 import (
    Condition,
    DataStoreClient,
    Outcome,
    Status,
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
    """Main function to demonstrate V2 data publishing and querying."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grpc-target",
        default="",
        help="gRPC target of a V2 service, such as [::1]:59606. Uses discovery when omitted.",
    )
    args = parser.parse_args()

    # The clients do not close a channel that they did not create, so close it here.
    grpc_channel = grpc.insecure_channel(args.grpc_target) if args.grpc_target else None
    try:
        published_measurement_id = publish_data(grpc_channel)
        query_data(published_measurement_id, grpc_channel)
    finally:
        if grpc_channel is not None:
            grpc_channel.close()


def publish_data(grpc_channel: grpc.Channel | None) -> str:
    """Demonstrate V2 data publishing of an AnalogWaveform."""
    with (
        MetadataStoreClient(grpc_channel=grpc_channel) as metadata_store_client,
        DataStoreClient(grpc_channel=grpc_channel) as data_store_client,
    ):
        # Create UUT instance
        uut = Uut(model_name="NI-6508", family="Digital")
        uut_id = metadata_store_client.create_uut(uut)
        uut_instance = UutInstance(uut_id=uut_id, serial_number="A861-42367")
        uut_instance_id = metadata_store_client.create_uut_instance(uut_instance=uut_instance)

        # Create Operator metadata
        operator = Operator(name="James Bowery", role="Test Operator")
        operator_id = metadata_store_client.create_operator(operator)
        print(f"created operator_id: {operator_id}")

        # Create TestStation metadata
        test_station = TestStation(name="TestStation_12")
        test_station_id = metadata_store_client.create_test_station(test_station)
        print(f"created test_station_id: {test_station_id}")

        # Create SoftwareItem metadata
        software_item = SoftwareItem(product="Windows", version="10.0.19044")
        software_item_id = metadata_store_client.create_software_item(software_item)
        print(f"created software_item_id: {software_item_id}")
        software_item_2 = SoftwareItem(product="Python", version="3.12")
        software_item_2_id = metadata_store_client.create_software_item(software_item_2)
        print(f"created software_item_2_id: {software_item_2_id}")

        # Create TestResult. In V2, status tracks progress separately from the outcome.
        test_result = TestResult(
            name="sample test result",
            operator_id=operator_id,
            test_station_id=test_station_id,
            software_item_ids=[software_item_id, software_item_2_id],
            uut_instance_id=uut_instance_id,
            status=Status.RUNNING,
        )
        test_result_id = data_store_client.create_test_result(test_result)
        print(f"created test_result_id: {test_result_id}")

        # Create the step. In V2, conditions belong to the step.
        step = Step(
            name="Initial step",
            test_result_id=test_result_id,
            conditions=[
                Condition("Ambient Temperature", 23.0, condition_type="Environment", units="degC")
            ],
        )
        step_id = data_store_client.create_step(step)

        name = "data publish sample"
        # Create waveform data to publish
        waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
            timing=Timing.create_with_regular_interval(
                ht.timedelta(seconds=1e-3), ht.datetime.now(timezone.utc)
            ),
        )

        # Create the measurement with the waveform data
        published_measurement_id = data_store_client.create_measurement(
            name=name,
            value=waveform,
            step_id=step_id,
            units="V",
            outcome=Outcome.PASSED,
        )
        published_measurement = data_store_client.get_measurement(published_measurement_id)
        print(
            f"Published measurement: '{published_measurement.name}' with id {published_measurement.id}"
        )

        # Mark the test result as done now that publishing is complete.
        data_store_client.update_test_result(
            test_result_id, status=Status.DONE, outcome=Outcome.PASSED
        )

    return published_measurement_id


def query_data(published_measurement_id: str, grpc_channel: grpc.Channel | None) -> None:
    """Demonstrate querying a published AnalogWaveform measurement."""
    with (
        MetadataStoreClient(grpc_channel=grpc_channel) as metadata_store_client,
        DataStoreClient(grpc_channel=grpc_channel) as data_store_client,
    ):
        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=Id eq {published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)

        if found_measurement is not None:
            print(
                f"Found published measurement: '{found_measurement.name}' with id {found_measurement.id}"
            )
            test_result = data_store_client.get_test_result(found_measurement.test_result_id)
            print(f"test_result: {test_result.name} ({test_result.status.name})")
            operator = metadata_store_client.get_operator(test_result.operator_id)
            print(f"operator: {operator}")

            step = data_store_client.get_step(found_measurement.step_id, read_fields=["conditions"])
            for condition in step.conditions:
                print(f"condition: {condition.name} = {condition.value} {condition.units}")

            waveform = data_store_client.read_measurement_value(
                found_measurement, expected_type=AnalogWaveform
            )
            print(f"published data is: {waveform.raw_data}")


if __name__ == "__main__":
    main()
