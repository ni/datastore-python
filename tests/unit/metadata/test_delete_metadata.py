"""Tests for deleting metadata through the metadata store client."""

from __future__ import annotations

from unittest.mock import NonCallableMock

import pytest
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    BatchDeleteAliasesRequest,
    BatchDeleteHardwareItemsRequest,
    BatchDeleteOperatorsRequest,
    BatchDeleteSchemasRequest,
    BatchDeleteSoftwareItemsRequest,
    BatchDeleteTestAdaptersRequest,
    BatchDeleteTestDescriptionsRequest,
    BatchDeleteTestStationsRequest,
    BatchDeleteTestsRequest,
    BatchDeleteUutInstancesRequest,
    BatchDeleteUutsRequest,
    DeleteAliasRequest,
    DeleteHardwareItemRequest,
    DeleteOperatorRequest,
    DeleteSchemaRequest,
    DeleteSoftwareItemRequest,
    DeleteTestAdapterRequest,
    DeleteTestDescriptionRequest,
    DeleteTestRequest,
    DeleteTestStationRequest,
    DeleteUutInstanceRequest,
    DeleteUutRequest,
)

from ni.datastore.metadata import MetadataStoreClient


DELETE_CASES = (
    pytest.param(
        "delete_uut_instance",
        {"uut_instance_id": "instance-id", "force": True},
        DeleteUutInstanceRequest(uut_instance_id="instance-id", force=True),
        id="delete_uut_instance",
    ),
    pytest.param(
        "delete_uut",
        {"uut_id": "uut-id", "force": True},
        DeleteUutRequest(uut_id="uut-id", force=True),
        id="delete_uut",
    ),
    pytest.param(
        "delete_operator",
        {"operator_id": "operator-id", "force": True},
        DeleteOperatorRequest(operator_id="operator-id", force=True),
        id="delete_operator",
    ),
    pytest.param(
        "delete_operator",
        {"operator_id": "operator-id"},
        DeleteOperatorRequest(operator_id="operator-id"),
        id="delete_operator_default_force",
    ),
    pytest.param(
        "delete_test_description",
        {"test_description_id": "description-id", "force": True},
        DeleteTestDescriptionRequest(test_description_id="description-id", force=True),
        id="delete_test_description",
    ),
    pytest.param(
        "delete_test",
        {"test_id": "test-id", "force": True},
        DeleteTestRequest(test_id="test-id", force=True),
        id="delete_test",
    ),
    pytest.param(
        "delete_test_station",
        {"test_station_id": "station-id", "force": True},
        DeleteTestStationRequest(test_station_id="station-id", force=True),
        id="delete_test_station",
    ),
    pytest.param(
        "delete_hardware_item",
        {"hardware_item_id": "hardware-id", "force": True},
        DeleteHardwareItemRequest(hardware_item_id="hardware-id", force=True),
        id="delete_hardware_item",
    ),
    pytest.param(
        "delete_software_item",
        {"software_item_id": "software-id", "force": True},
        DeleteSoftwareItemRequest(software_item_id="software-id", force=True),
        id="delete_software_item",
    ),
    pytest.param(
        "delete_test_adapter",
        {"test_adapter_id": "adapter-id", "force": True},
        DeleteTestAdapterRequest(test_adapter_id="adapter-id", force=True),
        id="delete_test_adapter",
    ),
    pytest.param(
        "delete_schema",
        {"schema_id": "schema-id"},
        DeleteSchemaRequest(schema_id="schema-id"),
        id="delete_schema",
    ),
    pytest.param(
        "batch_delete_uut_instances",
        {"uut_instance_ids": ["instance-1", "instance-2"], "force": True},
        BatchDeleteUutInstancesRequest(
            requests=[
                DeleteUutInstanceRequest(uut_instance_id="instance-1", force=True),
                DeleteUutInstanceRequest(uut_instance_id="instance-2", force=True),
            ]
        ),
        id="batch_delete_uut_instances",
    ),
    pytest.param(
        "batch_delete_uuts",
        {"uut_ids": ["uut-1", "uut-2"], "force": True},
        BatchDeleteUutsRequest(
            requests=[
                DeleteUutRequest(uut_id="uut-1", force=True),
                DeleteUutRequest(uut_id="uut-2", force=True),
            ]
        ),
        id="batch_delete_uuts",
    ),
    pytest.param(
        "batch_delete_operators",
        {"operator_ids": ["operator-1", "operator-2"], "force": True},
        BatchDeleteOperatorsRequest(
            requests=[
                DeleteOperatorRequest(operator_id="operator-1", force=True),
                DeleteOperatorRequest(operator_id="operator-2", force=True),
            ]
        ),
        id="batch_delete_operators",
    ),
    pytest.param(
        "batch_delete_test_descriptions",
        {"test_description_ids": ["description-1", "description-2"], "force": True},
        BatchDeleteTestDescriptionsRequest(
            requests=[
                DeleteTestDescriptionRequest(test_description_id="description-1", force=True),
                DeleteTestDescriptionRequest(test_description_id="description-2", force=True),
            ]
        ),
        id="batch_delete_test_descriptions",
    ),
    pytest.param(
        "batch_delete_tests",
        {"test_ids": ["test-1", "test-2"], "force": True},
        BatchDeleteTestsRequest(
            requests=[
                DeleteTestRequest(test_id="test-1", force=True),
                DeleteTestRequest(test_id="test-2", force=True),
            ]
        ),
        id="batch_delete_tests",
    ),
    pytest.param(
        "batch_delete_tests",
        {"test_ids": ["test-1", "test-2"]},
        BatchDeleteTestsRequest(
            requests=[
                DeleteTestRequest(test_id="test-1"),
                DeleteTestRequest(test_id="test-2"),
            ]
        ),
        id="batch_delete_tests_default_force",
    ),
    pytest.param(
        "batch_delete_test_stations",
        {"test_station_ids": ["station-1", "station-2"], "force": True},
        BatchDeleteTestStationsRequest(
            requests=[
                DeleteTestStationRequest(test_station_id="station-1", force=True),
                DeleteTestStationRequest(test_station_id="station-2", force=True),
            ]
        ),
        id="batch_delete_test_stations",
    ),
    pytest.param(
        "batch_delete_hardware_items",
        {"hardware_item_ids": ["hardware-1", "hardware-2"], "force": True},
        BatchDeleteHardwareItemsRequest(
            requests=[
                DeleteHardwareItemRequest(hardware_item_id="hardware-1", force=True),
                DeleteHardwareItemRequest(hardware_item_id="hardware-2", force=True),
            ]
        ),
        id="batch_delete_hardware_items",
    ),
    pytest.param(
        "batch_delete_software_items",
        {"software_item_ids": ["software-1", "software-2"], "force": True},
        BatchDeleteSoftwareItemsRequest(
            requests=[
                DeleteSoftwareItemRequest(software_item_id="software-1", force=True),
                DeleteSoftwareItemRequest(software_item_id="software-2", force=True),
            ]
        ),
        id="batch_delete_software_items",
    ),
    pytest.param(
        "batch_delete_test_adapters",
        {"test_adapter_ids": ["adapter-1", "adapter-2"], "force": True},
        BatchDeleteTestAdaptersRequest(
            requests=[
                DeleteTestAdapterRequest(test_adapter_id="adapter-1", force=True),
                DeleteTestAdapterRequest(test_adapter_id="adapter-2", force=True),
            ]
        ),
        id="batch_delete_test_adapters",
    ),
    pytest.param(
        "batch_delete_schemas",
        {"schema_ids": ["schema-1", "schema-2"]},
        BatchDeleteSchemasRequest(
            requests=[
                DeleteSchemaRequest(schema_id="schema-1"),
                DeleteSchemaRequest(schema_id="schema-2"),
            ]
        ),
        id="batch_delete_schemas",
    ),
    pytest.param(
        "batch_delete_aliases",
        {"alias_names": ["alias-1", "alias-2"]},
        BatchDeleteAliasesRequest(
            requests=[
                DeleteAliasRequest(alias_name="alias-1"),
                DeleteAliasRequest(alias_name="alias-2"),
            ]
        ),
        id="batch_delete_aliases",
    ),
)


@pytest.mark.parametrize(("method_name", "kwargs", "expected_request"), DELETE_CASES)
def test___delete_metadata___forwards_request(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    method_name: str,
    kwargs: dict[str, object],
    expected_request: object,
) -> None:
    result = getattr(metadata_store_client, method_name)(**kwargs)

    getattr(mocked_metadata_store_service_client, method_name).assert_called_once_with(
        expected_request
    )
    assert result is None
