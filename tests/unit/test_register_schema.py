"""Contains tests for validating schema registration."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import NonCallableMock

from ni.datastore import (
    Client,
)
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    RegisterSchemaRequest,
)


def test___register_schema_from_path____calls_metadatastoreclient_with_file_contents(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    client.register_schema(schema_path)

    args, __ = mocked_metadatastore_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema_from_string_path____calls_metadatastoreclient_with_file_contents(
    client: Client, mocked_metadatastore_client: NonCallableMock, schemas_directory: Path
) -> None:
    schema_path = schemas_directory / "hardware_item_schema.toml"

    client.register_schema(str(schema_path))

    args, __ = mocked_metadatastore_client.register_schema.call_args
    request = cast(RegisterSchemaRequest, args[0])
    assert request.schema == schema_path.read_text()


def test___register_schema_from_schema_contents____calls_metadatastoreclient_with_schema_contents(
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

    schema_id = client.register_schema(schema_path)

    assert schema_id == expected_schema_id
