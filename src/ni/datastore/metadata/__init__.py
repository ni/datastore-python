"""Public API for accessing the NI Metadata Store."""

from ni.datastore.metadata._metadata_store_client import MetadataStoreClient
from ni.datastore.metadata._types._alias import Alias
from ni.datastore.metadata._types._extension_schema import ExtensionSchema
from ni.datastore.metadata._types._hardware_item import HardwareItem
from ni.datastore.metadata._types._operator import Operator
from ni.datastore.metadata._types._software_item import SoftwareItem
from ni.datastore.metadata._types._test import Test
from ni.datastore.metadata._types._test_adapter import TestAdapter
from ni.datastore.metadata._types._test_description import TestDescription
from ni.datastore.metadata._types._test_station import TestStation
from ni.datastore.metadata._types._uut import Uut
from ni.datastore.metadata._types._uut_instance import UutInstance
from ni.measurements.metadata.v1.metadata_store_pb2 import AliasTargetType

__all__ = [
    "MetadataStoreClient",
    "Alias",
    "AliasTargetType",
    "ExtensionSchema",
    "HardwareItem",
    "Operator",
    "SoftwareItem",
    "Test",
    "TestAdapter",
    "TestDescription",
    "TestStation",
    "Uut",
    "UutInstance",
]

# Hide that it was not defined in this top-level package
MetadataStoreClient.__module__ = __name__
Alias.__module__ = __name__
AliasTargetType.__module__ = __name__
ExtensionSchema.__module__ = __name__
HardwareItem.__module__ = __name__
Operator.__module__ = __name__
SoftwareItem.__module__ = __name__
Test.__module__ = __name__
TestAdapter.__module__ = __name__
TestDescription.__module__ = __name__
TestStation.__module__ = __name__
Uut.__module__ = __name__
UutInstance.__module__ = __name__
