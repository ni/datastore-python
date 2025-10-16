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
    # TestAdapter,
    TestDescription,
    TestStation,
    Uut,
    UutInstance,
)
from nitypes.waveform import AnalogWaveform


def test___waveform_with_metadata___publish___query_read_returns_correct_data() -> None:
    with MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        # Metadata: UUT
        uut = Uut(
            model_name="NI-9205",
            family="Analog",
            manufacturers=["Manufacturer A", "Manufacturer B"],
            part_number="Part Number",
            link="Uut Link",
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
        )
        uut_instance_id = metadata_store_client.create_uut_instance(uut_instance=uut_instance)

        # Metadata: Operator
        operator_name = "John Bowery"
        operator_role = "Test Operator II"
        operator = Operator(operator_name=operator_name, role=operator_role)
        operator_id = metadata_store_client.create_operator(operator)

        # Create TestStation metadata
        test_station = TestStation(test_station_name="TestStation_12")
        test_station_id = metadata_store_client.create_test_station(test_station)

        # Test Description metadata
        # This only works when I provide an absolute path to the schema.
        current_directory = os.path.dirname(os.path.abspath(__file__))
        description_schema_id = metadata_store_client.register_schema_from_file(
            os.path.join(current_directory, "schemas", "test_description_schema.toml")
        )
        test_description = TestDescription(
            uut_id=uut_id,
            test_description_name="Metadata Acceptance Test",
            link="Test Description Link",
            extensions={"td1": "one", "td2": "two"},
            schema_id=description_schema_id,
        )
        test_description_id = metadata_store_client.create_test_description(test_description)

        # Create SoftwareItem metadata
        software_item = SoftwareItem(product="Windows", version="10.0.19044")
        software_item_id = metadata_store_client.create_software_item(software_item)
        software_item_2 = SoftwareItem(product="Python", version="3.12")
        software_item_2_id = metadata_store_client.create_software_item(software_item_2)
        software_item_ids = [software_item_id, software_item_2_id]

        # Create HardwareItem metadata
        hardware_item = HardwareItem(
            manufacturer="Test Manufacturer",
            model="Test Model",
            serial_number="Test Serial Number",
            part_number="Test Part Number",
            asset_identifier="Test Asset Identifier",
            calibration_due_date="Test Calibration Due Date",
            link="Hardware Item Link",
        )
        hardware_item_id = metadata_store_client.create_hardware_item(hardware_item)
        hardware_item_ids = [hardware_item_id]

        # Create TestAdapter metadata
        # test_adapter=TestAdapter(
        #     test_adapter_name="Test Adapter Name",
        #     manufacturer="Test Adapter Manufacturer",
        #     serial_number="Test Adapter Serial Number",
        #     part_number="Test Adapter Part Number",
        #     asset_identifier="Test Adapter Asset Identifier",
        #     calibration_due_date="Test Adapter Calibration Due Date",
        #     link="Test Adapter Link",
        # )
        # test_adapter_id = metadata_store_client.create_test_adapter(test_adapter)
        # test_adapter_ids = [test_adapter_id]

        # Create TestResult metadata
        test_result_name = "sample test result"
        found_test_result = TestResult(
            uut_instance_id=uut_instance_id,
            operator_id=operator_id,
            test_station_id=test_station_id,
            test_description_id=test_description_id,
            software_item_ids=software_item_ids,
            hardware_item_ids=hardware_item_ids,
            # test_adapter_ids=test_adapter_ids,
            test_result_name=test_result_name,
            link="Test Result Link",
        )
        test_result_id = data_store_client.create_test_result(found_test_result)

        # Create waveform data to publish
        expected_waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
        )

        # Create Test metadata
        test = Test(test_name="Test Name", description="Test Description", link="Test Link")
        test_id = metadata_store_client.create_test(test)

        # Publish the waveform data
        step = Step(
            # TODO: This has to be a valid UUID, not just a string.
            # parent_step_id="Parent Step Id",
            test_result_id=test_result_id,
            test_id=test_id,
            step_name="Step Name",
            step_type="Step Type",
            notes="Step Notes",
            link="Step Link",
        )
        step_id = data_store_client.create_step(step)

        timestamp = ht.datetime.now(tz=dt.timezone.utc)
        error_information = ErrorInformation(
            error_code=123, message="Error Message", source="Error Source"
        )

        published_measurement = data_store_client.publish_measurement(
            measurement_name="Measurement Name",
            value=expected_waveform,
            step_id=step_id,
            timestamp=timestamp,
            outcome=Outcome.OUTCOME_PASSED,
            error_information=error_information,
            hardware_item_ids=hardware_item_ids,
            # test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
            notes="Measurement Notes",
        )

        published_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {published_measurement.published_measurement_id}"
        )
        found_measurement = next(iter(published_measurements), None)
        assert found_measurement is not None

        # Assert on PublishedMeasurement fields
        assert found_measurement.measurement_notes == "Measurement Notes"
        assert found_measurement.measurement_name == "Measurement Name"
        assert sorted(found_measurement.software_item_ids) == sorted(software_item_ids)
        assert sorted(found_measurement.hardware_item_ids) == sorted(hardware_item_ids)
        # assert found_measurement.test_adapter_ids == test_adapter_ids
        assert found_measurement.error_information == error_information
        assert found_measurement.outcome == Outcome.OUTCOME_PASSED
        assert isinstance(found_measurement.start_date_time, ht.datetime)
        # We can't directly compare these datetimes because of bruising when converting
        # to bintime and back.
        assert found_measurement.start_date_time.day == timestamp.day

        # Assert on TestResult fields.
        found_test_result = data_store_client.get_test_result(found_measurement.test_result_id)
        assert found_test_result.test_result_name == test_result_name
        assert found_test_result.operator_id == operator_id
        assert sorted(found_test_result.software_item_ids) == sorted(software_item_ids)
        assert sorted(found_test_result.hardware_item_ids) == sorted(hardware_item_ids)
        # assert sorted(queried_test_result.test_adapter_ids) == sorted(test_adapter_ids)
        assert found_test_result.test_description_id == test_description_id
        assert found_test_result.test_station_id == test_station_id
        assert found_test_result.uut_instance_id == uut_instance_id

        # Asserts for Operator
        found_operator = metadata_store_client.get_operator(found_test_result.operator_id)
        assert found_operator.operator_name == operator.operator_name
        assert found_operator.role == operator.role

        # Asserts for UutInstance
        found_uut_instance = metadata_store_client.get_uut_instance(
            found_test_result.uut_instance_id
        )
        assert found_uut_instance.serial_number == uut_instance.serial_number
        assert found_uut_instance.uut_id == uut_instance.uut_id
        assert found_uut_instance.firmware_version == uut_instance.firmware_version
        assert found_uut_instance.manufacture_date == uut_instance.manufacture_date
        assert found_uut_instance.hardware_version == uut_instance.hardware_version

        # Asserts for Uut
        found_uut = metadata_store_client.get_uut(found_uut_instance.uut_id)
        assert found_uut.model_name == uut.model_name
        # TODO: GH Issue - https://github.com/ni/datastore-python/issues/47
        assert found_uut.family == uut.family
        # TODO: File an issue about found_uut.manufacturers being a blank list.
        # assert found_uut.manufacturers == uut.manufacturers
        assert found_uut.part_number == uut.part_number
        assert found_uut.link == uut.link

        # Asserts for TestStation
        found_test_station = metadata_store_client.get_test_station(found_test_result.test_station_id)
        assert found_test_station.test_station_name == test_station.test_station_name

        waveform = data_store_client.read_data(found_measurement, expected_type=AnalogWaveform)
        assert waveform == expected_waveform
