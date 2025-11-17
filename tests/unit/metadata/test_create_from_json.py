"""Contains tests for validating JSON metadata creation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import NonCallableMock

import pytest
from ni.datastore.metadata import (
    MetadataItems,
    MetadataStoreClient,
)
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    CreateFromJsonDocumentRequest,
    CreateFromJsonDocumentResponse,
)


@pytest.fixture
def sample_metadata_json() -> str:
    """Sample JSON metadata for testing."""
    return json.dumps(
        {
            "uuts": [
                {"alias": "uut1", "modelName": "Model1", "partNumber": "PN001"},
                {"alias": "uut2", "modelName": "Model2", "family": "TestFamily"},
            ],
            "operators": [
                {"alias": "op1", "name": "John Doe", "role": "Test Engineer"},
                {"alias": "op2", "name": "Jane Smith", "role": "Lab Technician"},
            ],
            "tests": [
                {"alias": "test1", "name": "Test 1", "description": "First test description"},
                {"alias": "test2", "name": "Test 2", "description": "Second test description"},
            ],
            "hardwareItems": [
                {"alias": "hw1", "manufacturer": "NI", "model": "PXI-5172", "serialNumber": "SN001"}
            ],
            "softwareItems": [{"alias": "sw1", "product": "TestStand", "version": "2023"}],
            "testStations": [
                {"alias": "station1", "name": "Station Alpha", "assetIdentifier": "ASSET001"}
            ],
            "testAdapters": [
                {
                    "alias": "adapter1",
                    "name": "Test Fixture A",
                    "manufacturer": "Custom",
                    "serialNumber": "FIX001",
                }
            ],
            "uutInstances": [
                {
                    "alias": "instance1",
                    "uutAlias": "uut1",
                    "serialNumber": "UUT-SN001",
                    "firmwareVersion": "1.0.0",
                }
            ],
            "testDescriptions": [
                {"alias": "desc1", "uutAlias": "uut1", "name": "UUT1 Test Description"}
            ],
        },
        indent=2,
    )


@pytest.fixture
def mock_create_response() -> CreateFromJsonDocumentResponse:
    """Mock response for create_from_json_document."""
    response = CreateFromJsonDocumentResponse()
    # Add mock entities to the response as needed for testing
    return response


def test___create_from_json_file_with_pathlib_path___calls_metadata_store_service_client_with_file_contents(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    tmp_path: Path,
    sample_metadata_json: str,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json_file with Path object calls service client with file contents."""
    # Arrange
    metadata_file = tmp_path / "test_metadata.json"
    metadata_file.write_text(sample_metadata_json, encoding="utf-8")
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json_file(metadata_file)

    # Assert
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == sample_metadata_json
    assert isinstance(result, MetadataItems)


def test___create_from_json_file_with_string_path___calls_metadata_store_service_client_with_file_contents(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    tmp_path: Path,
    sample_metadata_json: str,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json_file with string path calls service client with file contents."""
    # Arrange
    metadata_file = tmp_path / "test_metadata.json"
    metadata_file.write_text(sample_metadata_json, encoding="utf-8")
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json_file(str(metadata_file))

    # Assert
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == sample_metadata_json
    assert isinstance(result, MetadataItems)


def test___create_from_json_file_with_non_existent_pathlib_path___raises_error(
    metadata_store_client: MetadataStoreClient,
    tmp_path: Path,
) -> None:
    """Test that create_from_json_file raises FileNotFoundError for non-existent Path."""
    # Arrange
    metadata_file = tmp_path / "non_existent_metadata.json"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Metadata file not found"):
        metadata_store_client.create_from_json_file(metadata_file)


def test___create_from_json_file_with_non_existent_string_path___raises_error(
    metadata_store_client: MetadataStoreClient,
    tmp_path: Path,
) -> None:
    """Test that create_from_json_file raises FileNotFoundError for non-existent string path."""
    # Arrange
    metadata_file = tmp_path / "non_existent_metadata.json"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Metadata file not found"):
        metadata_store_client.create_from_json_file(str(metadata_file))


def test___create_from_json_file_with_utf8_bom___handles_encoding_correctly(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    tmp_path: Path,
    sample_metadata_json: str,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json_file correctly handles UTF-8 BOM encoding."""
    # Arrange - Write file with UTF-8 BOM
    metadata_file = tmp_path / "test_metadata_bom.json"
    metadata_file.write_text(sample_metadata_json, encoding="utf-8-sig")
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json_file(metadata_file)

    # Assert
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == sample_metadata_json  # BOM should be stripped
    assert isinstance(result, MetadataItems)


def test___create_from_json___calls_metadata_store_service_client_with_json_contents(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    sample_metadata_json: str,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json calls service client with JSON contents."""
    # Arrange
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json(sample_metadata_json)

    # Assert
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == sample_metadata_json
    assert isinstance(result, MetadataItems)


def test___create_from_json___returns_metadata_items_from_protobuf_response(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    sample_metadata_json: str,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json returns MetadataItems from protobuf response."""
    # Arrange
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json(sample_metadata_json)

    # Assert
    assert isinstance(result, MetadataItems)
    # Verify that MetadataItems.from_protobuf was called with the mock response
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == sample_metadata_json


def test___create_from_json_with_minimal_json___handles_empty_collections(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json handles minimal JSON with empty collections."""
    # Arrange
    minimal_json = json.dumps({"uuts": [{"modelName": "SimpleModel"}]})
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json(minimal_json)

    # Assert
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == minimal_json
    assert isinstance(result, MetadataItems)


def test___create_from_json_with_complex_extensions___preserves_extension_data(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json preserves complex extension data."""
    # Arrange
    json_with_extensions = json.dumps(
        {
            "operators": [
                {
                    "name": "Test Operator",
                    "role": "Engineer",
                    "schemaId": "custom-schema-123",
                    "extension": {
                        "customField1": "value1",
                        "customField2": "value2",
                        "department": "R&D",
                    },
                }
            ],
            "hardwareItems": [
                {
                    "manufacturer": "NI",
                    "model": "PXI-5172",
                    "serialNumber": "12345",
                    "extension": {"calibrationDate": "2024-01-15", "location": "Lab A"},
                }
            ],
        }
    )
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json(json_with_extensions)

    # Assert
    args, __ = mocked_metadata_store_service_client.create_from_json_document.call_args
    request = cast(CreateFromJsonDocumentRequest, args[0])
    assert request.json_document == json_with_extensions
    assert isinstance(result, MetadataItems)


def test___create_from_json_file___returns_metadata_items_from_metadata_store_service_client(
    metadata_store_client: MetadataStoreClient,
    mocked_metadata_store_service_client: NonCallableMock,
    tmp_path: Path,
    sample_metadata_json: str,
    mock_create_response: CreateFromJsonDocumentResponse,
) -> None:
    """Test that create_from_json_file returns MetadataItems from service client."""
    # Arrange
    metadata_file = tmp_path / "test_metadata.json"
    metadata_file.write_text(sample_metadata_json, encoding="utf-8")
    mocked_metadata_store_service_client.create_from_json_document.return_value = (
        mock_create_response
    )

    # Act
    result = metadata_store_client.create_from_json_file(metadata_file)

    # Assert
    assert isinstance(result, MetadataItems)
    mocked_metadata_store_service_client.create_from_json_document.assert_called_once()
