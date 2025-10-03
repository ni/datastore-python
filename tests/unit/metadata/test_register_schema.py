"""Contains tests for validating schema registration."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import NonCallableMock

import pytest
from ni.datastore.metadata import (
    MetadataStoreClient,
)
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    RegisterSchemaRequest,
)


def test___register_schema_from_file_with_pathlib_path___calls_metadata_store_service_client_with_file_contents(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    schemas_directory: Path,
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    metadata_store_client.register_schema_from_file(schema_path)

    args, __ = mocked_metadata_store_service_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema_from_file_with_string_path___calls_metadata_store_service_client_with_file_contents(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    schemas_directory: Path,
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    metadata_store_client.register_schema_from_file(str(schema_path))

    args, __ = mocked_metadata_store_service_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema_from_file_with_non_existent_pathlib_path___raises_error(
    metadata_store_client: MetadataStoreClient, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "non_existent_schema.toml"

    with pytest.raises(FileNotFoundError):
        metadata_store_client.register_schema_from_file(schema_path)


def test___register_schema_from_file_with_non_existent_string_path___raises_error(
    metadata_store_client: MetadataStoreClient, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "non_existent_schema.toml"

    with pytest.raises(FileNotFoundError):
        metadata_store_client.register_schema_from_file(str(schema_path))


def test___register_schema_from_file___returns_schema_id_from_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    schemas_directory: Path,
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"
    expected_schema_id = "schema_id_123"
    mocked_metadata_store_service_client.register_schema.return_value.schema_id = expected_schema_id

    schema_id = metadata_store_client.register_schema_from_file(schema_path)

    assert schema_id == expected_schema_id


def test___register_schema___calls_metadata_store_service_client_with_schema_contents(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    schemas_directory: Path,
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    metadata_store_client.register_schema(schema_path.read_text())

    args, __ = mocked_metadata_store_service_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema___returns_schema_id_from_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    schemas_directory: Path,
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"
    expected_schema_id = "schema_id_123"
    mocked_metadata_store_service_client.register_schema.return_value.schema_id = expected_schema_id

    schema_id = metadata_store_client.register_schema(schema_path.read_text())

    assert schema_id == expected_schema_id
