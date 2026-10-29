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

`delete_test_result`, `delete_step`, and `delete_measurement` remove resources.
Without `force=True`, deleting a test result with steps, or a step with
measurements, fails with `FAILED_PRECONDITION`; with `force=True`, the owned
children are deleted too. A step that has child steps cannot be deleted.

The client wraps every method of the V2 low-level client:

- `remove_condition` removes a condition from a step.
- `add_test_result_metadata`, `remove_test_result_metadata`,
  `add_measurement_metadata`, and `remove_measurement_metadata` link or unlink
  software items, hardware items, and test adapters after creation. As defined
  by DEC-017, `remove_test_result_metadata` raises `ValueError`, without
  removing anything, if a measurement of the test result still references an
  item; unlink it from those measurements first. If the test result's
  measurements come back across more than one page of query results, it raises
  `RuntimeError` instead of removing, because the check cannot be completed.
- `create_measurement` accepts `upper_limit` and `lower_limit` of any supported
  value type. The service stores the limits as given and does not compare them
  with the value. `read_measurement_values` returns the value and both limits.
- `batch_create_*`, `batch_update_*`, and `batch_delete_*` handle many test
  results, steps, or measurements in one atomic call. Batch updates take a
  dictionary of fields keyed by ID, and batch deletes accept one `force` flag or
  one flag per ID.
- `TestResult.steps`, `Step.children`, and `Step.measurements` create a whole
  tree in one call. Metadata objects such as `Operator` or `SoftwareItem` can be
  passed instead of IDs to find or create them.
- `create_measurement` accepts `SoftwareItem`, `HardwareItem`, and
  `TestAdapter` objects for inline find-or-create, in addition to their IDs.
- `query_*` methods return `QueryResults`, a list with a `next_link` attribute
  that is set when the service has more results.
- JSON values and conditions accept a plain dictionary, or `JsonValue` when the
  value needs attributes. Reads return a `JsonValue` only when attributes are
  present.

## V1 Convenience Differences

- V1 `publish_condition` and `publish_condition_batch` do not have direct V2
  equivalents. V2 conditions belong to a step; use `add_condition(step_id, ...)`
  to add or replace one. Read conditions through the containing step returned
  by `get_step` or `query_steps`; there are no standalone V2 condition get/query
  methods in this high-level API.
- V1 `publish_measurement_batch` is shaped for parametric sweeps. In V2, use
  `batch_create_measurements` with `Measurement` objects; each item can target a
  different step, and the whole batch is atomic.
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
  Python or nitypes values. A single value is always read back as a `Scalar`,
  with or without units, and a list of values as a `Vector`. When a `Scalar` is
  given and `units` is not, the measurement's `units` are taken from the
  `Scalar`. Conditions accept scalar or JSON values. A scalar condition value
  reads back as a plain Python value, or as a `Scalar` when it has extended
  properties other than units. JSON values
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
- `status` and `outcome` are separate, but the service requires status `DONE`
  (or no status) whenever a test result or step has an outcome other than
  `UNSPECIFIED`. For example, `status=Status.RUNNING` with
  `outcome=Outcome.FAILED` is rejected with `INVALID_ARGUMENT`.
- When you pass your own `grpc_channel`, gRPC limits received messages to 4 MB
  by default, so reading a large value such as a 1-million-sample waveform fails
  with `RESOURCE_EXHAUSTED`. Create the channel with
  `options=[("grpc.max_receive_message_length", -1)]` to remove the limit. The
  default discovery path already does this.
- Waveform values read back with the same data, but their timing start time is a
  `nitypes.bintime.DateTime` rather than a `hightime.datetime`. As a result, `==`
  between a published waveform and the one read back returns `False`; compare
  the data, such as `raw_data`, instead.
