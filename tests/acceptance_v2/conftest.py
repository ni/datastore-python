"""Fixtures for acceptance tests that require a V2 Data Store service."""

from typing import Generator

import grpc
import pytest
from ni.measurementlink.discovery.v1.client import DiscoveryClient
from utilities import DataStoreContext

from ni.datastore.metadata import MetadataStoreClient


@pytest.fixture(scope="module")
def acceptance_test_context(
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[DataStoreContext, None, None]:
    """Set up isolated discovery and storage settings for the V2 service tests."""
    base_directory = tmp_path_factory.mktemp("v2-data-store")
    with DataStoreContext(base_directory, api_mode="v2") as data_store_context:
        yield data_store_context


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark V2 tests so default pytest runs can exclude this suite."""
    for item in items:
        if "tests/acceptance_v2/" in item.nodeid.replace("\\", "/"):
            item.add_marker(pytest.mark.acceptance_v2)


@pytest.fixture
def metadata_store_client(
    acceptance_test_context: DataStoreContext,
) -> Generator[MetadataStoreClient, None, None]:
    """Connect metadata operations to the V2 Data Store's Metadata Store interface."""
    discovery_client = DiscoveryClient()
    compute_nodes = discovery_client.enumerate_compute_nodes()
    remote_nodes = [node for node in compute_nodes if not node.is_local]
    deployment_target = remote_nodes[0].url if len(remote_nodes) == 1 else ""
    service_location = discovery_client.resolve_service(
        provided_interface="ni.measurements.metadata.v1.MetadataStoreService",
        service_class="ni.measurements.data.v2.DataStoreService",
        deployment_target=deployment_target,
    )
    grpc_channel = grpc.insecure_channel(service_location.insecure_address)
    try:
        with MetadataStoreClient(grpc_channel=grpc_channel) as metadata_store_client:
            yield metadata_store_client
    finally:
        grpc_channel.close()
