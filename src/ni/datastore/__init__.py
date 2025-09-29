"""Public API for accessing the NI Data Store Service."""

from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.datastore._client import Client
from ni.datastore._types._alias import Alias
from ni.datastore._types._extension_schema import ExtensionSchema
from ni.datastore._types._hardware_item import HardwareItem
from ni.datastore._types._operator import Operator
from ni.datastore._types._published_condition import PublishedCondition
from ni.datastore._types._published_measurement import PublishedMeasurement
from ni.datastore._types._software_item import SoftwareItem
from ni.datastore._types._step import Step
from ni.datastore._types._test import Test
from ni.datastore._types._test_adapter import TestAdapter
from ni.datastore._types._test_description import TestDescription
from ni.datastore._types._test_result import TestResult
from ni.datastore._types._test_station import TestStation
from ni.datastore._types._uut import Uut
from ni.datastore._types._uut_instance import UutInstance
from ni.measurements.data.v1.data_store_pb2 import ErrorInformation, Outcome
from ni.measurements.metadata.v1.metadata_store_pb2 import AliasTargetType

__all__ = [
    "Client",
    "Alias",
    "AliasTargetType",
    "ErrorInformation",
    "ExtensionSchema",
    "HardwareItem",
    "Moniker",
    "Operator",
    "Outcome",
    "PublishedCondition",
    "PublishedMeasurement",
    "SoftwareItem",
    "Step",
    "Test",
    "TestAdapter",
    "TestDescription",
    "TestResult",
    "TestStation",
    "Uut",
    "UutInstance",
]

# Hide that it was not defined in this top-level package
Client.__module__ = __name__
Alias.__module__ = __name__
AliasTargetType.__module__ = __name__
ErrorInformation.__module__ = __name__
ExtensionSchema.__module__ = __name__
HardwareItem.__module__ = __name__
Moniker.__module__ = __name__
Operator.__module__ = __name__
Outcome.__module__ = __name__
PublishedCondition.__module__ = __name__
PublishedMeasurement.__module__ = __name__
SoftwareItem.__module__ = __name__
Step.__module__ = __name__
Test.__module__ = __name__
TestAdapter.__module__ = __name__
TestDescription.__module__ = __name__
TestResult.__module__ = __name__
TestStation.__module__ = __name__
Uut.__module__ = __name__
UutInstance.__module__ = __name__
