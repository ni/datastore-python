"""How to detect, publish, and query system hardware and software resources."""

import os
import platform
from dataclasses import dataclass

import nisyscfg
import nisyscfg.component_info
import nisyscfg.hardware_resource
from ni.datastore.data import (
    DataStoreClient,
    TestResult,
)
from ni.datastore.metadata import (
    HardwareItem,
    MetadataStoreClient,
    Operator,
    SoftwareItem,
    TestStation,
)


@dataclass(frozen=True)
class SystemMetadata:
    """Represents the available resources on a system."""

    operator: Operator
    test_station: TestStation
    hardware_items: list[HardwareItem]
    software_items: list[SoftwareItem]


def main() -> None:
    """Detect, publish, and query hardware and software resources from the local system."""
    print("Scanning system for metadata...")
    system_metadata = detect_system_resources()

    print("Publishing detected system metadata...")
    test_result_id = publish_empty_test_result(system_metadata)

    print("Querying system metadata...")
    test_result = query_test_result(test_result_id)

    print()
    print(f"TestResult ID: {test_result.id}")
    print(f"- Operator: {test_result.operator_id}")
    print(f"- Test Station: {test_result.test_station_id}")
    print(f"- Installed Software: {len(test_result.software_item_ids)} packages")
    print(f"- Available Hardware: {len(test_result.hardware_item_ids)} devices")


def detect_system_resources(system_target: str = "localhost") -> SystemMetadata:
    """Scan the specified system_target and return SystemMetadata describing the system."""
    with nisyscfg.Session(target=system_target) as session:
        ni_device_filter = session.create_filter()
        ni_device_filter.is_ni_product = True
        ni_device_filter.is_device = True
        ni_device_filter.is_present = True

        operator = create_operator()
        test_station = create_test_station(session)
        hardware = [
            create_hardware_item(entry) for entry in session.find_hardware(ni_device_filter)
        ]
        software = [
            create_software_item(entry) for entry in session.get_installed_software_components()
        ]
        system_metadata = SystemMetadata(operator, test_station, hardware, software)
    return system_metadata


def create_hardware_item(
    hardware_entry: nisyscfg.hardware_resource.HardwareResource,
) -> HardwareItem:
    """Create a new HardwareItem instance from the specified nisyscfg entry."""
    manufacturer = hardware_entry.vendor_name
    model = hardware_entry.product_name
    serial_number = hardware_entry.serial_number
    new_instance = HardwareItem(manufacturer=manufacturer, model=model, serial_number=serial_number)
    return new_instance


def create_software_item(software_entry: nisyscfg.component_info.ComponentInfo) -> SoftwareItem:
    """Create a new SoftwareItem instance from the specified nisyscfg entry."""
    new_instance = SoftwareItem(product=software_entry.id, version=software_entry.version)
    return new_instance


def create_test_station(session: nisyscfg.Session) -> TestStation:
    """Create a new TestStation instance from the specified nisyscfg session."""
    new_instance = TestStation(name=session.hostname)
    return new_instance


def create_operator(name: str = "") -> Operator:
    """Create a new Operator instance using the specified name. Otherwise, use the active user."""
    if not name:
        host_os = platform.system()
        if host_os == "Windows":
            username_variable = "USERNAME"
        elif host_os == "Linux":
            username_variable = "USER"
        else:
            raise NotImplementedError(f"{host_os} support not implemented")
        name = os.environ.get(username_variable, "Unknown operator")

    new_instance = Operator(name=name)
    return new_instance


def publish_empty_test_result(system_metadata: SystemMetadata) -> str:
    """Publish a TestResult with the specified system_metadata and return its ID."""
    with MetadataStoreClient() as metadata_store_client:
        operator_id = metadata_store_client.create_operator(system_metadata.operator)
        test_station_id = metadata_store_client.create_test_station(system_metadata.test_station)
        hardware_item_ids = [
            metadata_store_client.create_hardware_item(entry)
            for entry in system_metadata.hardware_items
        ]
        software_item_ids = [
            metadata_store_client.create_software_item(entry)
            for entry in system_metadata.software_items
        ]

    empty_result = TestResult(
        name="system metadata result",
        operator_id=operator_id,
        test_station_id=test_station_id,
        software_item_ids=software_item_ids,
        hardware_item_ids=hardware_item_ids,
    )

    with DataStoreClient() as datastore_client:
        test_result_id = datastore_client.create_test_result(empty_result)

    return test_result_id


def query_test_result(test_result_id: str) -> TestResult:
    """Query the NI DataStore Service for the specified TestResult and return it."""
    with DataStoreClient() as datastore_client:
        test_result = datastore_client.get_test_result(test_result_id)
    return test_result


if __name__ == "__main__":
    main()
