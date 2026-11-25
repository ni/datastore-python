"""Acceptance test for V2 publishing with metadata references and extensions."""

import datetime as dt
import os

import hightime as ht
import numpy as np
from nitypes.waveform import AnalogWaveform, NoneScaleMode, SampleIntervalMode, Timing
from utilities import DataStoreContext

from ni.datastore.data.v2 import (
    DataStoreClient,
    ErrorInformation,
    MeasurementField,
    Outcome,
    StepField,
    TestResult,
    TestResultField,
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
from tests.acceptance._utils import append_hashed_time


def test___metadata_mutations___link_read_and_unlink_metadata(
    acceptance_test_context: DataStoreContext,
) -> None:
    description = append_hashed_time("v2 metadata mutations")

    with MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        software_item_id = metadata_store_client.create_software_item(
            SoftwareItem(product="Acceptance test software", version="1.0")
        )
        test_result = data_store_client.create_test_result(f"{description} test result")
        step = data_store_client.create_step(f"{description} step", test_result_id=test_result.id)
        measurement = data_store_client.create_measurement(
            f"{description} measurement", 1.0, step.id
        )

        data_store_client.add_test_result_metadata(
            test_result.id, software_item_ids=[software_item_id]
        )
        data_store_client.add_measurement_metadata(
            measurement.id, software_item_ids=[software_item_id]
        )

        found_test_result = data_store_client.get_test_result(
            test_result.id, read_fields=[TestResultField.SOFTWARE_ITEM_IDS]
        )
        found_measurement = data_store_client.get_measurement(
            measurement.id,
            read_fields=[
                MeasurementField.ID,
                MeasurementField.NAME,
                MeasurementField.SOFTWARE_ITEM_IDS,
            ],
        )
        assert found_test_result.software_item_ids == [software_item_id]
        assert found_measurement.id == measurement.id
        assert found_measurement.name == measurement.name
        assert found_measurement.software_item_ids == [software_item_id]

        data_store_client.remove_measurement_metadata(
            measurement.id, software_item_ids=[software_item_id]
        )
        data_store_client.remove_test_result_metadata(
            test_result.id, software_item_ids=[software_item_id]
        )

        found_test_result = data_store_client.get_test_result(
            test_result.id, read_fields=[TestResultField.SOFTWARE_ITEM_IDS]
        )
        found_measurement = data_store_client.get_measurement(
            measurement.id, read_fields=[MeasurementField.SOFTWARE_ITEM_IDS]
        )
        assert not found_test_result.software_item_ids
        assert not found_measurement.software_item_ids


def test___waveform_with_all_metadata___publish___query_read_returns_correct_data(
    acceptance_test_context: DataStoreContext,
) -> None:
    with MetadataStoreClient() as metadata_store_client, DataStoreClient() as data_store_client:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        schema_id = metadata_store_client.register_schema_from_file(
            os.path.join(
                os.path.dirname(current_directory), "acceptance", "schemas", "extensions.toml"
            )
        )

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
        uut_instance_id = metadata_store_client.create_uut_instance(uut_instance)
        operator = Operator(
            name="John Bowery",
            role="Test Operator II",
            extension={"o1": "one", "o2": "two"},
            schema_id=schema_id,
        )
        operator_id = metadata_store_client.create_operator(operator)
        test_station = TestStation(
            name="TestStation_12",
            asset_identifier="Test Station Asset Identifier",
            link="Test Station Link",
            extension={"ts1": "one", "ts2": "two"},
            schema_id=schema_id,
        )
        test_station_id = metadata_store_client.create_test_station(test_station)
        test_description = TestDescription(
            uut_id=uut_id,
            name="Metadata Acceptance Test",
            link="Test Description Link",
            extension={"td1": "one", "td2": "two"},
            schema_id=schema_id,
        )
        test_description_id = metadata_store_client.create_test_description(test_description)
        software_item = SoftwareItem(
            product="Windows",
            version="10.0.19044",
            link="Windows Link",
            extension={"sw1": "one", "sw2": "two"},
            schema_id=schema_id,
        )
        software_item_id = metadata_store_client.create_software_item(software_item)
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

        description = append_hashed_time("v2 metadata test result")
        test_result = data_store_client.create_test_result(
            TestResult(
                name=description,
                uut_instance_id=uut_instance_id,
                uut_id=uut_id,
                operator_id=operator_id,
                test_station_id=test_station_id,
                test_description_id=test_description_id,
                software_item_ids=[software_item_id],
                hardware_item_ids=[hardware_item_id],
                test_adapter_ids=[test_adapter_id],
                link="Test Result Link",
                extension={"tr1": "one", "tr2": "two"},
            )
        )
        test = Test(
            name="Test Name",
            description="Test Description",
            link="Test Link",
            extension={"t1": "one", "t2": "two"},
            schema_id=schema_id,
        )
        test_id = metadata_store_client.create_test(test)
        parent_step = data_store_client.create_step("Parent Step", test_result_id=test_result.id)
        step = data_store_client.create_step(
            "Step Name",
            parent_step_id=parent_step.id,
            test_result_id=test_result.id,
            test_id=test_id,
            step_type="Step Type",
            notes="Step Notes",
            link="Step Link",
            extension={"s1": "one", "s2": "two"},
        )
        expected_waveform = AnalogWaveform(
            sample_count=3,
            raw_data=np.array([1.0, 2.0, 3.0]),
            scale_mode=NoneScaleMode(),
            timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
        )
        timestamp = ht.datetime.now(tz=dt.timezone.utc)
        error_information = ErrorInformation(
            error_code=123, message="Error Message", source="Error Source"
        )
        measurement = data_store_client.create_measurement(
            "Measurement Name",
            expected_waveform,
            step.id,
            start_date_time=timestamp,
            outcome=Outcome.PASSED,
            error_information=error_information,
            hardware_item_ids=[hardware_item_id],
            test_adapter_ids=[test_adapter_id],
            software_item_ids=[software_item_id],
            notes="Measurement Notes",
        )

        queried_measurements = data_store_client.query_measurements(
            odata_query=f"$filter=id eq {measurement.id}",
            read_fields=[
                MeasurementField.ID,
                MeasurementField.TEST_RESULT_ID,
                MeasurementField.STEP_ID,
                MeasurementField.NAME,
                MeasurementField.NOTES,
                MeasurementField.SOFTWARE_ITEM_IDS,
                MeasurementField.HARDWARE_ITEM_IDS,
                MeasurementField.TEST_ADAPTER_IDS,
                MeasurementField.ERROR_INFORMATION,
                MeasurementField.OUTCOME,
                MeasurementField.START_DATE_TIME,
            ],
        )
        assert len(queried_measurements) == 1
        found_measurement = queried_measurements[0]
        assert found_measurement.notes == "Measurement Notes"
        assert found_measurement.name == "Measurement Name"
        assert sorted(found_measurement.software_item_ids) == [software_item_id]
        assert sorted(found_measurement.hardware_item_ids) == [hardware_item_id]
        assert found_measurement.test_adapter_ids == [test_adapter_id]
        assert found_measurement.error_information == error_information
        assert found_measurement.outcome == Outcome.PASSED
        assert isinstance(found_measurement.start_date_time, ht.datetime)
        assert found_measurement.start_date_time.day == timestamp.day

        found_test_result = data_store_client.get_test_result(
            found_measurement.test_result_id,
            read_fields=[
                TestResultField.NAME,
                TestResultField.OPERATOR_ID,
                TestResultField.SOFTWARE_ITEM_IDS,
                TestResultField.HARDWARE_ITEM_IDS,
                TestResultField.TEST_DESCRIPTION_ID,
                TestResultField.TEST_STATION_ID,
                TestResultField.UUT_INSTANCE_ID,
                TestResultField.UUT_ID,
                TestResultField.EXTENSION,
            ],
        )
        assert found_test_result.name == description
        assert found_test_result.operator_id == operator_id
        assert sorted(found_test_result.software_item_ids) == [software_item_id]
        assert sorted(found_test_result.hardware_item_ids) == [hardware_item_id]
        assert found_test_result.test_description_id == test_description_id
        assert found_test_result.test_station_id == test_station_id
        assert found_test_result.uut_instance_id == uut_instance_id
        assert found_test_result.uut_id == uut_id
        assert found_test_result.extension == test_result.extension
        found_step = data_store_client.get_step(
            found_measurement.step_id,
            read_fields=[
                StepField.PARENT_STEP_ID,
                StepField.TEST_RESULT_ID,
                StepField.TEST_ID,
                StepField.NAME,
                StepField.STEP_TYPE,
                StepField.NOTES,
                StepField.LINK,
                StepField.EXTENSION,
            ],
        )
        assert found_step.parent_step_id == step.parent_step_id
        assert found_step.test_result_id == step.test_result_id
        assert found_step.test_id == step.test_id
        assert found_step.name == step.name
        assert found_step.step_type == step.step_type
        assert found_step.notes == step.notes
        assert found_step.link == step.link
        assert found_step.extension == step.extension

        found_test = metadata_store_client.get_test(found_step.test_id)
        assert found_test.description == test.description
        assert found_test.name == test.name
        assert found_test.link == test.link
        assert found_test.extension == test.extension

        found_operator = metadata_store_client.get_operator(found_test_result.operator_id)
        assert found_operator.name == operator.name
        assert found_operator.role == operator.role
        assert found_operator.extension == operator.extension

        found_uut_instance = metadata_store_client.get_uut_instance(
            found_test_result.uut_instance_id
        )
        assert found_uut_instance.serial_number == uut_instance.serial_number
        assert found_uut_instance.uut_id == uut_instance.uut_id
        assert found_uut_instance.firmware_version == uut_instance.firmware_version
        assert found_uut_instance.manufacture_date == uut_instance.manufacture_date
        assert found_uut_instance.hardware_version == uut_instance.hardware_version
        assert found_uut_instance.extension == uut_instance.extension

        found_uut = metadata_store_client.get_uut(found_uut_instance.uut_id)
        assert found_uut.model_name == uut.model_name
        assert found_uut.family == uut.family
        assert found_uut.part_number == uut.part_number
        assert found_uut.link == uut.link
        assert found_uut.extension == uut.extension

        found_test_station = metadata_store_client.get_test_station(
            found_test_result.test_station_id
        )
        assert found_test_station.name == test_station.name
        assert found_test_station.asset_identifier == test_station.asset_identifier
        assert found_test_station.link == test_station.link
        assert found_test_station.extension == test_station.extension

        found_test_description = metadata_store_client.get_test_description(
            found_test_result.test_description_id
        )
        assert found_test_description.name == test_description.name
        assert found_test_description.link == test_description.link
        assert found_test_description.extension == test_description.extension

        found_software_item = metadata_store_client.get_software_item(
            found_test_result.software_item_ids[0]
        )
        assert found_software_item.product == software_item.product
        assert found_software_item.version == software_item.version
        assert found_software_item.link == software_item.link
        assert found_software_item.extension == software_item.extension

        found_hardware_item = metadata_store_client.get_hardware_item(
            found_test_result.hardware_item_ids[0]
        )
        assert found_hardware_item.manufacturer == hardware_item.manufacturer
        assert found_hardware_item.model == hardware_item.model
        assert found_hardware_item.serial_number == hardware_item.serial_number
        assert found_hardware_item.part_number == hardware_item.part_number
        assert found_hardware_item.asset_identifier == hardware_item.asset_identifier
        assert found_hardware_item.calibration_due_date == hardware_item.calibration_due_date
        assert found_hardware_item.link == hardware_item.link
        assert found_hardware_item.extension == hardware_item.extension

        read_waveform = data_store_client.read_measurement_value(
            found_measurement.id, AnalogWaveform
        )
        assert read_waveform == expected_waveform
