"""Acceptance test that publishes then queries waveform data and metadata."""

import datetime as dt
import os

import hightime as ht
import numpy as np
from ni.datastore.data import (
    DataStoreClient,
    ErrorInformation,
    Outcome,
    Step,
    TestResult,
)
from ni.datastore.metadata import (
    HardwareItem,
    MetadataStoreClient,
    Operator,
    SoftwareItem,
    Test,
    TestAdapter,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)
from nitypes.waveform import AnalogWaveform

from examples.common import DataStoreContext


def test___waveform_with_all_metadata___publish___query_read_returns_correct_data() -> None:
    with DataStoreContext(), MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        # Load the extensions schema
        current_directory = os.path.dirname(os.path.abspath(__file__))
        schema_id = metadata_store_client.register_schema_from_file(
            os.path.join(current_directory, "schemas", "extensions.toml")
        )

        # Metadata: UUT
        uut = Uut(
            model_name="NI-9205",
            family="Analog",
            manufacturers=["Manufacturer A", "Manufacturer B"],
            part_number="Part Number",
            link="Uut Link",
            extension={"u1": "one", "u2": "two"},
            schema_id=schema_id,
        )
        uut_id = metadata_store_client.create_uut(uut)

        # Metadata: UUTInstance
        uut_instance = UutInstance(
            uut_id=uut_id,
            serial_number="A861-12345",
            manufacture_date="Manufacture Date",
            firmware_version="Firmware Version",
            hardware_version="Hardware Version",
            link="UutInstance Link",
            extension={"ui1": "one", "ui2": "two"},
            schema_id=schema_id,
        )
        uut_instance_id = metadata_store_client.create_uut_instance(uut_instance=uut_instance)

        # Metadata: Operator
        operator_name = "John Bowery"
        operator_role = "Test Operator II"
        operator = Operator(
            name=operator_name,
            role=operator_role,
            extension={"o1": "one", "o2": "two"},
            schema_id=schema_id,
        )
        operator_id = metadata_store_client.create_operator(operator)

        # Metadata: TestStation
        test_station = TestStation(
            name="TestStation_12",
            asset_identifier="Test Station Asset Identifier",
            link="Test Station Link",
            extension={"ts1": "one", "ts2": "two"},
            schema_id=schema_id,
        )
        test_station_id = metadata_store_client.create_test_station(test_station)

        # Metadata: TestDescription
        test_description = TestDescription(
            uut_id=uut_id,
            name="Metadata Acceptance Test",
            link="Test Description Link",
            extension={"td1": "one", "td2": "two"},
            schema_id=schema_id,
        )
        test_description_id = metadata_store_client.create_test_description(test_description)

        # Metadata: SoftwareItem
        software_item = SoftwareItem(
            product="Windows",
            version="10.0.19044",
            link="Windows Link",
            extension={"sw1": "one", "sw2": "two"},
            schema_id=schema_id,
        )
        software_item_id = metadata_store_client.create_software_item(software_item)
        software_item_ids = [software_item_id]

        # Metadata: HardwareItem
        hardware_item = HardwareItem(
            manufacturer="Test Manufacturer",
            model="Test Model",
            serial_number="Test Serial Number",
            part_number="Test Part Number",
            asset_identifier="Test Asset Identifier",
            calibration_due_date="Test Calibration Due Date",
            link="Hardware Item Link",
            extension={"hw1": "one", "hw2": "two"},
            schema_id=schema_id,
        )
        hardware_item_id = metadata_store_client.create_hardware_item(hardware_item)
        hardware_item_ids = [hardware_item_id]

        # Metadata: TestAdapter
        test_adapter = TestAdapter(
            name="Test Adapter Name",
            manufacturer="Test Adapter Manufacturer",
            serial_number="Test Adapter Serial Number",
            part_number="Test Adapter Part Number",
            asset_identifier="Test Adapter Asset Identifier",
            calibration_due_date="Test Adapter Calibration Due Date",
            link="Test Adapter Link",
        )
        test_adapter_id = metadata_store_client.create_test_adapter(test_adapter)
        test_adapter_ids = [test_adapter_id]

        # Metadata: TestResult
        test_result_name = "sample test result"
        test_result = TestResult(
            uut_instance_id=uut_instance_id,
            operator_id=operator_id,
            test_station_id=test_station_id,
            test_description_id=test_description_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            name=test_result_name,
            link="Test Result Link",
            extension={"tr1": "one", "tr2": "two"},
            schema_id=schema_id,
        )
        test_result_id = data_store_client.create_test_result(test_result)

        # Data: Waveform data to publish
        expected_waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
        )

        # Metadata: Test
        test = Test(
            name="Test Name",
            description="Test Description",
            link="Test Link",
            extension={"t1": "one", "t2": "two"},
            schema_id=schema_id,
        )
        test_id = metadata_store_client.create_test(test)

        # Data: Step
        parent_step = Step(name="Parent Step")
        step = Step(
            parent_step_id=parent_step.id,
            test_result_id=test_result_id,
            test_id=test_id,
            name="Step Name",
            step_type="Step Type",
            notes="Step Notes",
            link="Step Link",
            extension={"s1": "one", "s2": "two"},
            schema_id=schema_id,
        )
        step_id = data_store_client.create_step(step)

        timestamp = ht.datetime.now(tz=dt.timezone.utc)
        error_information = ErrorInformation(
            error_code=123, message="Error Message", source="Error Source"
        )

        # Perform publish operation
        published_measurement_id = data_store_client.publish_measurement(
            name="Measurement Name",
            value=expected_waveform,
            step_id=step_id,
            timestamp=timestamp,
            outcome=Outcome.PASSED,
            error_information=error_information,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
            notes="Measurement Notes",
        )

        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # Check PublishedMeasurement
        assert found_measurement.notes == "Measurement Notes"
        assert found_measurement.name == "Measurement Name"
        assert sorted(found_measurement.software_item_ids) == sorted(software_item_ids)
        assert sorted(found_measurement.hardware_item_ids) == sorted(hardware_item_ids)
        assert found_measurement.test_adapter_ids == test_adapter_ids
        assert found_measurement.error_information == error_information
        assert found_measurement.outcome == Outcome.PASSED
        assert isinstance(found_measurement.start_date_time, ht.datetime)
        # We can't directly compare these datetimes because of bruising when converting
        # to bintime and back.
        assert found_measurement.start_date_time.day == timestamp.day

        # Check TestResult
        found_test_result = data_store_client.get_test_result(found_measurement.test_result_id)
        assert found_test_result.name == test_result_name
        assert found_test_result.operator_id == operator_id
        assert sorted(found_test_result.software_item_ids) == sorted(software_item_ids)
        assert sorted(found_test_result.hardware_item_ids) == sorted(hardware_item_ids)
        # assert sorted(queried_test_result.test_adapter_ids) == sorted(test_adapter_ids)
        assert found_test_result.test_description_id == test_description_id
        assert found_test_result.test_station_id == test_station_id
        assert found_test_result.uut_instance_id == uut_instance_id
        assert found_test_result.extension == test_result.extension

        # Check Step
        found_step = data_store_client.get_step(found_measurement.step_id)
        assert found_step.parent_step_id == step.parent_step_id
        assert found_step.test_result_id == step.test_result_id
        assert found_step.test_id == step.test_id
        assert found_step.name == step.name
        assert found_step.step_type == step.step_type
        assert found_step.notes == step.notes
        assert found_step.link == step.link
        assert found_step.extension == step.extension

        # Check Test
        found_test = metadata_store_client.get_test(found_step.test_id)
        assert found_test.description == test.description
        assert found_test.name == test.name
        assert found_test.link == test.link
        assert found_test.extension == test.extension

        # Check Operator
        found_operator = metadata_store_client.get_operator(found_test_result.operator_id)
        assert found_operator.name == operator.name
        assert found_operator.role == operator.role
        assert found_operator.extension == operator.extension

        # Check UutInstance
        found_uut_instance = metadata_store_client.get_uut_instance(
            found_test_result.uut_instance_id
        )
        assert found_uut_instance.serial_number == uut_instance.serial_number
        assert found_uut_instance.uut_id == uut_instance.uut_id
        assert found_uut_instance.firmware_version == uut_instance.firmware_version
        assert found_uut_instance.manufacture_date == uut_instance.manufacture_date
        assert found_uut_instance.hardware_version == uut_instance.hardware_version
        assert found_uut_instance.extension == uut_instance.extension

        # Check Uut
        found_uut = metadata_store_client.get_uut(found_uut_instance.uut_id)
        assert found_uut.model_name == uut.model_name
        assert found_uut.family == uut.family
        # TODO: File an issue about found_uut.manufacturers being a blank list.
        # assert found_uut.manufacturers == uut.manufacturers
        assert found_uut.part_number == uut.part_number
        assert found_uut.link == uut.link
        assert found_uut.extension == uut.extension

        # Check TestStation
        found_test_station = metadata_store_client.get_test_station(
            found_test_result.test_station_id
        )
        assert found_test_station.name == test_station.name
        assert found_test_station.asset_identifier == test_station.asset_identifier
        assert found_test_station.link == test_station.link
        assert found_test_station.extension == test_station.extension

        # Check TestDescription
        found_test_description = metadata_store_client.get_test_description(
            found_test_result.test_description_id
        )
        assert found_test_description.name == test_description.name
        assert found_test_description.link == test_description.link
        assert found_test_description.extension == test_description.extension

        # Check SoftwareItem
        found_sw_item = metadata_store_client.get_software_item(
            found_test_result.software_item_ids[0]
        )
        assert found_sw_item.product == software_item.product
        assert found_sw_item.version == software_item.version
        assert found_sw_item.link == software_item.link
        assert found_sw_item.extension == software_item.extension

        # Check HardwareItem
        found_hw_item = metadata_store_client.get_hardware_item(
            found_test_result.hardware_item_ids[0]
        )
        assert found_hw_item.manufacturer == hardware_item.manufacturer
        assert found_hw_item.model == hardware_item.model
        assert found_hw_item.serial_number == hardware_item.serial_number
        assert found_hw_item.part_number == hardware_item.part_number
        assert found_hw_item.asset_identifier == hardware_item.asset_identifier
        assert found_hw_item.calibration_due_date == hardware_item.calibration_due_date
        assert found_hw_item.link == hardware_item.link
        assert found_hw_item.extension == hardware_item.extension

        waveform = data_store_client.read_data(found_measurement, expected_type=AnalogWaveform)
        assert waveform == expected_waveform
