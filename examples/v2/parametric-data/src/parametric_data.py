"""Publish and query a parametric audio-amplifier test with the V2 APIs."""

import argparse
import platform

import grpc

from ni.datastore.data.v2 import Condition, DataStoreClient, Outcome, Status, Step, TestResult
from ni.datastore.metadata import (
    MetadataStoreClient,
    Operator,
    SoftwareItem,
    TestStation,
    Uut,
    UutInstance,
)

from nitypes.scalar import Scalar

AMBIENT_TEMPERATURES = (25.0, 50.0)
SUPPLY_VOLTAGES = (12.0, 15.0, 18.0)
TEST_STATIONS = ("Amplifier Bench A", "Amplifier Bench B")


def main() -> None:
    """Run and read back the amplifier parametric sweep."""
    args = _parse_args()
    grpc_channel = grpc.insecure_channel(args.grpc_target) if args.grpc_target else None
    try:
        _run_parametric_sweep(grpc_channel)
    finally:
        if grpc_channel is not None:
            grpc_channel.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grpc-target",
        default="",
        help="gRPC target of a V2 service, such as [::1]:59606. Uses discovery when omitted.",
    )
    return parser.parse_args()


def _run_parametric_sweep(grpc_channel: grpc.Channel | None) -> None:
    with (
        MetadataStoreClient(grpc_channel=grpc_channel) as metadata_store_client,
        DataStoreClient(grpc_channel=grpc_channel) as data_store_client,
    ):
        print("Preparing amplifier and test metadata")
        test_results = _create_test_results(metadata_store_client, data_store_client)

        measurement_count = 0
        print("\nPublishing output-voltage measurements")
        for station_name, test_result_id in test_results:
            print(f"  Publishing at {station_name}")
            measurement_count += _publish_sweep(data_store_client, test_result_id)
            data_store_client.update_test_result(
                test_result_id, status=Status.DONE, outcome=Outcome.PASSED
            )
        print(
            f"Published {measurement_count} measurements across "
            f"{len(test_results)} test stations"
        )

        print("\nReading back published measurements")
        _read_sweep(metadata_store_client, data_store_client, test_results)
        print("Readback complete")


def _create_test_results(
    metadata_store_client: MetadataStoreClient, data_store_client: DataStoreClient
) -> list[tuple[str, str]]:
    """Create shared amplifier metadata and a test result for each station."""
    uut_id = metadata_store_client.create_uut(Uut(model_name="PA-120", family="Audio Amplifier"))
    uut_instance_id = metadata_store_client.create_uut_instance(
        UutInstance(uut_id=uut_id, serial_number="AMP-0042")
    )
    operator_id = metadata_store_client.create_operator(
        Operator(name="Example Operator", role="Test Operator")
    )
    software_item_ids = [
        metadata_store_client.create_software_item(
            SoftwareItem(product=platform.system(), version=platform.release())
        ),
        metadata_store_client.create_software_item(
            SoftwareItem(product="Python", version=platform.python_version())
        ),
    ]
    test_results = []
    for station_name in TEST_STATIONS:
        test_station_id = metadata_store_client.create_test_station(TestStation(name=station_name))
        print(f"  Created test station: {station_name}")
        test_result = TestResult(
            name=f"PA-120 Output Voltage Parametric Sweep - {station_name}",
            operator_id=operator_id,
            test_station_id=test_station_id,
            software_item_ids=software_item_ids,
            uut_instance_id=uut_instance_id,
            status=Status.RUNNING,
        )
        test_result_id = data_store_client.create_test_result(test_result)
        test_results.append((station_name, test_result_id))
        print(f"  Created test result: {test_result_id}")
    return test_results


def _publish_sweep(data_store_client: DataStoreClient, test_result_id: str) -> int:
    """Publish one scalar output-voltage measurement for every condition pair."""
    measurement_count = 0
    for ambient_temperature in AMBIENT_TEMPERATURES:
        for supply_voltage in SUPPLY_VOLTAGES:
            step = Step(
                name=f"Output at {ambient_temperature:g} degC, {supply_voltage:g} V",
                test_result_id=test_result_id,
                conditions=[
                    Condition(
                        "ambient_temperature",
                        ambient_temperature,
                        condition_type="Environment",
                        units="degC",
                    ),
                    Condition(
                        "supply_voltage",
                        supply_voltage,
                        condition_type="Setup",
                        units="V",
                    ),
                ],
            )
            step_id = data_store_client.create_step(step)
            output_voltage = _simulated_output_voltage(ambient_temperature, supply_voltage)
            data_store_client.create_measurement(
                name="output_voltage",
                value=output_voltage,
                step_id=step_id,
                units="V",
                outcome=Outcome.PASSED,
            )
            measurement_count += 1
    return measurement_count


def _simulated_output_voltage(ambient_temperature: float, supply_voltage: float) -> float:
    """Return representative 1 kHz amplifier output data in volts RMS."""
    temperature_drift = (ambient_temperature - 25.0) * 0.002
    return round(supply_voltage * 0.25 - temperature_drift, 2)


def _read_sweep(
    metadata_store_client: MetadataStoreClient,
    data_store_client: DataStoreClient,
    test_results: list[tuple[str, str]],
) -> None:
    """Query each station's measurements and include its metadata in the results."""
    rows: list[tuple[str, str, str, str]] = []
    for _, test_result_id in test_results:
        test_result = data_store_client.get_test_result(test_result_id)
        test_station = metadata_store_client.get_test_station(test_result.test_station_id)
        print(f"  Querying measurements for {test_station.name}")
        measurements = data_store_client.query_measurements(
            f"$filter=TestResultId eq {test_result_id}"
        )
        for measurement in measurements:
            step = data_store_client.get_step(measurement.step_id, read_fields=["conditions"])
            conditions = {condition.name: condition for condition in step.conditions}
            output_voltage = data_store_client.read_measurement_value(
                measurement, expected_type=Scalar
            )
            rows.append(
                (
                    test_station.name,
                    f"{conditions['ambient_temperature'].value:g}",
                    f"{conditions['supply_voltage'].value:g}",
                    f"{output_voltage.value:.2f}",
                )
            )
    rows.sort(key=lambda row: (row[0], float(row[1]), float(row[2])))
    _print_sweep_table(rows)


def _print_sweep_table(rows: list[tuple[str, str, str, str]]) -> None:
    headers = ("Test Station", "Temp (degC)", "Supply Voltage (V)", "Output Voltage (V)")
    widths = [
        max([len(header), *(len(row[index]) for row in rows)])
        for index, header in enumerate(headers)
    ]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    print(border)
    print("|" + "|".join(f" {header:<{width}} " for header, width in zip(headers, widths)) + "|")
    print(border)
    for row in rows:
        print(
            "|"
            + "|".join(
                f" {value:<{width}} " if index == 0 else f" {value:>{width}} "
                for index, (value, width) in enumerate(zip(row, widths))
            )
            + "|"
        )
    print(border)


if __name__ == "__main__":
    main()
