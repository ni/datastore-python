# NI Data Store V2 Python API

Use the separate V2 client when you need the V2 service model. Like the V1
client, it uses Python types (`TestResult`, `Step`, `Measurement`, `Condition`,
`ErrorInformation`, `Outcome`, and `Status`) and constructs the gRPC request
messages internally.

```python
from datetime import timezone

from hightime import datetime
from ni.datastore.data.v2 import (
    Condition,
    DataStoreClient,
    Measurement,
    Outcome,
    Status,
    Step,
    TestResult,
)

with DataStoreClient() as client:
    test_result_id = client.create_test_result(
        TestResult("Power test", start_date_time=datetime.now(tz=timezone.utc))
    )
    step_id = client.create_step(
        Step("Measure voltage", test_result_id=test_result_id, status=Status.RUNNING)
    )
    client.add_condition(
        step_id, Condition("supply-voltage", 5.0, condition_type="Nominal", units="V")
    )
    measurement_id = client.create_measurement(
        "voltage",
        5.02,
        step_id,
        units="V",
        outcome=Outcome.PASSED,
    )
    measurement = client.get_measurement(measurement_id)
    voltage = client.read_measurement_value(measurement)
```

The client also provides `get_test_result`, `get_step`, `query_test_results`,
`query_steps`, `query_measurements`, and update methods for test results, steps,
and measurements. These return the Python types, with timestamps as
`hightime.datetime`, durations as `hightime.timedelta`, and extensions as
dictionaries. Queries accept an OData expression and optional `read_fields`.
Updates accept mutable fields as keyword arguments and build the protobuf field
mask automatically. Empty updates and fields that the service does not allow to
change raise `ValueError` before an RPC is made.

## V1 Convenience Differences

- V1 `publish_condition` and `publish_condition_batch` do not have direct V2
  equivalents. V2 conditions belong to a step; use `add_condition(step_id, ...)`
  to add or replace one. Read conditions through the containing step returned
  by `get_step` or `query_steps`; there are no standalone V2 condition get/query
  methods in this high-level API.
- This high-level V2 API does not include the V1 batch-publish convenience.
  Call `create_measurement` once per measurement; these are separate service
  operations and are not atomic as a group.
- V2 has its own `TestResult`, `Step`, `Measurement`, `Condition`, and
  `ErrorInformation` types in `ni.datastore.data.v2`, because the V2 resource
  fields differ from V1. They follow the V1 style: create methods take them,
  and get/query/update methods return them instead of protobuf messages.
- V2 create and update methods accept `hightime.datetime` timestamps and
  `hightime.timedelta` durations, converted with the NI precision converters.
  Timestamps must use `datetime.timezone.utc`; other time zones are rejected.
  Round trips are exact to about 1 ns; finer precision is not preserved.
- Test results and steps accept `keywords`, and test results accept `uut_id`
  updates. Keywords, duration, and `uut_id` are stored once the service delivers
  the Stage 2 New Resource Fields feature.
- Measurement values are converted to scalar, vector, supported NI
  waveform-family, or JSON values; `read_measurement_value` converts them back to
  Python or nitypes values. Conditions accept scalar or JSON values. JSON values
  require the service's Stage 3 Structured JSON Storage And Query Support.
- Software item, hardware item, and test adapter IDs on a measurement must first
  be linked to its test result; pass them to `create_test_result`.
- Discovery, channel configuration, and cleanup are delegated to the low-level
  V2 client. Its gRPC transport exceptions pass through unchanged; invalid
  wrapper values and update fields fail locally with `TypeError` or
  `ValueError`. As in V1, calling a method after `close()` raises
  `RuntimeError`.
- V1 and V2 hosts both register the metadata store interface. When both run in
  the same discovery cluster, `MetadataStoreClient()` cannot choose between
  them; pass a `grpc_channel` for the intended host.
