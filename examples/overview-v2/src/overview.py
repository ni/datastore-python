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
    StepField,
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

# Remove gRPC's 4 MB receive limit so that large values, such as long waveforms, can be read.
_GRPC_OPTIONS = [("grpc.max_receive_message_length", -1)]


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
    grpc_channel = (
        grpc.insecure_channel(args.grpc_target, options=_GRPC_OPTIONS) if args.grpc_target else None
    )
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
        # A UUT describes a product model that many test results share, so create it once
        # and link it by ID. Each UUT instance refers to its UUT by ID.
        uut_id = metadata_store_client.create_uut(Uut(model_name="NI-6508", family="Digital"))

        # Create the TestResult with its metadata inline. The service finds a matching
        # operator, test station, UUT instance, or software item, or creates a new one.
        # In V2, status tracks progress separately from the outcome.
        test_result = TestResult(
            name="sample test result",
            uut_instance=UutInstance(uut_id=uut_id, serial_number="A861-42367"),
            operator=Operator(name="James Bowery", role="Test Operator"),
            test_station=TestStation(name="TestStation_12"),
            software_items=[
                SoftwareItem(product="Windows", version="10.0.19044"),
                SoftwareItem(product="Python", version="3.12"),
            ],
            status=Status.RUNNING,
        )
        created_test_result = data_store_client.create_test_result(test_result)
        print(f"created test_result_id: {created_test_result.id}")
        print(f"linked operator_id: {created_test_result.operator_id}")

        # Create the step. In V2, conditions belong to the step.
        step = Step(
            name="Initial step",
            test_result_id=created_test_result.id,
            conditions=[
                Condition("Ambient Temperature", 23.0, condition_type="Environment", units="degC")
            ],
        )
        created_step = data_store_client.create_step(step)

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
        published_measurement = data_store_client.create_measurement(
            name=name,
            value=waveform,
            step_id=created_step.id,
            units="V",
            outcome=Outcome.PASSED,
        )
        print(
            f"Published measurement: '{published_measurement.name}' with id {published_measurement.id}"
        )

        # Mark the test result as done now that publishing is complete.
        data_store_client.update_test_result(
            created_test_result.id, status=Status.DONE, outcome=Outcome.PASSED
        )

    return published_measurement.id


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

            step = data_store_client.get_step(
                found_measurement.step_id, read_fields=[StepField.CONDITIONS]
            )
            for condition in step.conditions:
                print(f"condition: {condition.name} = {condition.value} {condition.units}")

            waveform = data_store_client.read_measurement_value(
                found_measurement, expected_type=AnalogWaveform
            )
            print(f"published data is: {waveform.raw_data}")


if __name__ == "__main__":
    main()
