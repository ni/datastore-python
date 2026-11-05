"""Public API for accessing the NI Data Store V2."""

from ni.datastore.data.v2._data_store_client import DataStoreClient
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._create import StepCreateFields, TestResultCreateFields
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._json_value import JsonValue
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._measurement_value import (
    MeasurementReadValue,
    MeasurementValue,
)
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._query_results import QueryResults
from ni.datastore.data.v2._types._read_fields import (
    MeasurementField,
    MeasurementValueField,
    StepField,
    TestResultField,
)
from ni.datastore.data.v2._types._status import Status
from ni.datastore.data.v2._types._step import Step
from ni.datastore.data.v2._types._test_result import TestResult
from ni.datastore.data.v2._types._update import (
    MeasurementUpdateBuilder,
    MeasurementUpdateFields,
    StepUpdateBuilder,
    StepUpdateFields,
    TestResultUpdateBuilder,
    TestResultUpdateFields,
)

__all__ = [
    "Condition",
    "DataStoreClient",
    "ErrorInformation",
    "JsonValue",
    "Measurement",
    "MeasurementField",
    "MeasurementReadValue",
    "MeasurementUpdateBuilder",
    "MeasurementUpdateFields",
    "MeasurementValue",
    "MeasurementValueField",
    "Outcome",
    "QueryResults",
    "Status",
    "Step",
    "StepCreateFields",
    "StepField",
    "StepUpdateBuilder",
    "StepUpdateFields",
    "TestResult",
    "TestResultCreateFields",
    "TestResultField",
    "TestResultUpdateBuilder",
    "TestResultUpdateFields",
]

# Hide that it was not defined in this top-level package
Condition.__module__ = __name__
DataStoreClient.__module__ = __name__
ErrorInformation.__module__ = __name__
JsonValue.__module__ = __name__
Measurement.__module__ = __name__
MeasurementField.__module__ = __name__
MeasurementUpdateBuilder.__module__ = __name__
MeasurementUpdateFields.__module__ = __name__
MeasurementValueField.__module__ = __name__
Outcome.__module__ = __name__
QueryResults.__module__ = __name__
Status.__module__ = __name__
Step.__module__ = __name__
StepCreateFields.__module__ = __name__
StepField.__module__ = __name__
StepUpdateBuilder.__module__ = __name__
StepUpdateFields.__module__ = __name__
TestResult.__module__ = __name__
TestResultCreateFields.__module__ = __name__
TestResultField.__module__ = __name__
TestResultUpdateBuilder.__module__ = __name__
TestResultUpdateFields.__module__ = __name__
