"""Helper methods to convert between python and protobuf types."""

from __future__ import annotations

import logging
from typing import MutableMapping

from google.protobuf.internal.containers import MessageMap
from ni.measurements.metadata.v1.metadata_store_pb2 import ExtensionValue

_logger = logging.getLogger(__name__)


def populate_extension_value_message_map(
    destination: MessageMap[str, ExtensionValue],
    source: MutableMapping[str, str],
) -> None:
    """Populate a gRPC message map of string keys to ExtensionValue.

    The input is a mapping of string keys to string values.
    """
    for key, value in source.items():
        destination[key].string_value = value


def populate_from_extension_value_message_map(
    destination: MutableMapping[str, str],
    source: MessageMap[str, ExtensionValue],
) -> None:
    """Populate a mapping of string keys to stringvalues.

    The input is a gRPC message map of string keys to ExtensionValue.
    """
    for key, extension_value in source.items():
        value_case = extension_value.WhichOneof("metadata")
        if value_case == "string_value":
            destination[key] = extension_value.string_value
        else:
            raise TypeError(f"Unsupported ExtensionValue type for key '{key}': {value_case}")
