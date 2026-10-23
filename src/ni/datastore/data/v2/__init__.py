"""Public API for accessing the NI Data Store V2."""

from ni.datastore.data.v2._data_store_client import DataStoreClient
from ni.datastore.data.v2._types._condition import Condition
from ni.datastore.data.v2._types._error_information import ErrorInformation
from ni.datastore.data.v2._types._measurement import Measurement
from ni.datastore.data.v2._types._outcome import Outcome
from ni.datastore.data.v2._types._status import Status
from ni.datastore.data.v2._types._step import Step
from ni.datastore.data.v2._types._test_result import TestResult

__all__ = [
    "Condition",
    "DataStoreClient",
    "ErrorInformation",
    "Measurement",
    "Outcome",
    "Status",
    "Step",
    "TestResult",
]

# Hide that it was not defined in this top-level package
Condition.__module__ = __name__
DataStoreClient.__module__ = __name__
ErrorInformation.__module__ = __name__
Measurement.__module__ = __name__
Outcome.__module__ = __name__
Status.__module__ = __name__
Step.__module__ = __name__
TestResult.__module__ = __name__
