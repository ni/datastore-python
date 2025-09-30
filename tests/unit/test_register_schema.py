"""Contains tests for validating schema registration."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import NonCallableMock

import pytest
from ni.datastore import (
    Client,
)
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    RegisterSchemaRequest,
)


def test___register_schema_from_file_with_pathlib_path___calls_metadatastoreclient_with_file_contents(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    client.register_schema_from_file(schema_path)

    args, __ = mocked_metadatastore_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema_from_file_with_string_path___calls_metadatastoreclient_with_file_contents(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    client.register_schema_from_file(str(schema_path))

    args, __ = mocked_metadatastore_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema_from_file_with_non_existent_pathlib_path___throws_error(
    client: Client, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "non_existent_schema.toml"

    with pytest.raises(FileNotFoundError):
        client.register_schema_from_file(schema_path)


def test___register_schema_from_file_with_non_existent_string_path___throws_error(
    client: Client, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "non_existent_schema.toml"

    with pytest.raises(FileNotFoundError):
        client.register_schema_from_file(str(schema_path))


def test___register_schema_from_file___returns_schema_id_from_metadatastoreclient(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"
    expected_schema_id = "schema_id_123"
    mocked_metadatastore_client.register_schema.return_value.schema_id = expected_schema_id

    schema_id = client.register_schema_from_file(schema_path)

    assert schema_id == expected_schema_id


def test___register_schema___calls_metadatastoreclient_with_schema_contents(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    client.register_schema(schema_path.read_text())

    args, __ = mocked_metadatastore_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema___returns_schema_id_from_metadatastoreclient(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"
    expected_schema_id = "schema_id_123"
    mocked_metadatastore_client.register_schema.return_value.schema_id = expected_schema_id

    schema_id = client.register_schema(schema_path.read_text())

    assert schema_id == expected_schema_id
