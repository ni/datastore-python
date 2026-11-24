# NI Data Store V2 Python API

Use the V2 client when you need the V2 service model. It uses Python types
(`TestResult`, `Step`, `Measurement`, `Condition`,
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
    test_result = client.create_test_result(
        TestResult("Power test", start_date_time=datetime.now(tz=timezone.utc))
    )
    step = client.create_step(
        Step("Measure voltage", test_result_id=test_result.id, status=Status.RUNNING)
    )
    client.add_condition(
        step.id, Condition("supply-voltage", 5.0, condition_type="Nominal", units="V")
    )
    measurement = client.create_measurement(
        "voltage",
        5.02,
        step.id,
        units="V",
        outcome=Outcome.PASSED,
    )
    voltage = client.read_measurement_value(measurement)
```

Each create method accepts either the object or its fields as arguments, so
`client.create_step("Measure voltage", test_result_id=test_result.id)` and
`client.create_measurement(Measurement(name="voltage", value=5.02, step_id=step.id))`
also work. `add_condition` likewise accepts a `Condition`, or its name, value, and
fields, such as `client.add_condition(step.id, "supply-voltage", 5.0, units="V")`.
`TestResultCreateFields`, `StepCreateFields`, `MeasurementCreateFields`, and
`ConditionCreateFields` type the keyword fields.
Create methods return the created object as saved by the service, including its
generated ID. Nested resources, such as the steps of a test result, and expanded
metadata are not included. The client also provides `get_test_result`, `get_step`,
`query_test_results`, `query_steps`, `query_measurements`, and update methods for
test results, steps, and measurements. These return the Python types, with
timestamps as `hightime.datetime`, durations as `hightime.timedelta`, and
extensions as dictionaries. Queries accept an OData expression and optional
`read_fields`. Read fields are selected with `TestResultField`, `StepField`, or
`MeasurementField`, for example `read_fields=[StepField.CONDITIONS]`; field names
as strings are also accepted.

Measurements also accept optional classification labels through `keywords`; use
`read_fields=[MeasurementField.KEYWORDS]` to request them from a query or get.

Queries support pagination with `page_size` and `page_token`. A zero `page_size`
uses the service default. Pass the previous result's `next_page_token` to fetch
the following page:

```python
page = client.query_steps(page_size=100)
if page.next_page_token:
  next_page = client.query_steps(page_size=100, page_token=page.next_page_token)
```

`QueryResults.next_link` remains as a compatibility alias; new code should use
`next_page_token`.

`Step.has_children` is output-only and can be requested with
`read_fields=[StepField.HAS_CHILDREN]`. It becomes true after the step has had a
committed direct child and remains true even if that child is later deleted.
The installed V2 proto package must include the field for its value to be read;
older generated packages report it as false.

Updates change only the fields named in the protobuf update mask, and the client
builds the mask for you. Pass a `Step`, or its ID, with keyword fields, an update
builder, or the whole object:

```python
from ni.datastore.data.v2 import Outcome, StepUpdateBuilder

# Keyword fields: only these fields change. None clears a field.
data_store_client.update_step(step, notes="Verified", outcome=Outcome.PASSED)

# Update builder: each with_ call selects one field, like the .NET client builders.
update = StepUpdateBuilder(step).with_notes("Verified").with_outcome(Outcome.PASSED)
data_store_client.update_step(update)

# Whole object: every updatable field is set from the object, so empty fields are cleared.
step.notes = "Verified"
data_store_client.update_step(step)
```

Keyword fields are typed by `TestResultUpdateFields`, `StepUpdateFields`, and
`MeasurementUpdateFields`, so type checkers report unknown fields and wrong value
types. `TestResultUpdateBuilder`, `StepUpdateBuilder`, and
`MeasurementUpdateBuilder` follow the .NET builders: setting a relationship by ID,
such as `with_operator_id`, replaces inline metadata set earlier, and inline
metadata replaces an ID. A whole-object update sends Stage 2 fields (`keywords`,
`duration`, and `uut_id`/`uut`) only when they have a value, and sends only the ID
when a relationship has both an ID and inline metadata. Empty updates and fields
that the service does not allow to change raise `ValueError` before an RPC is made.

IDs can be passed as `str` or `uuid.UUID`, and reads return them as `str`.
Test result, step, and measurement IDs must be UUIDs. Metadata ID fields, such as
`operator_id` or `software_item_ids`, also accept registered aliases.

`delete_test_result`, `delete_step`, and `delete_measurement` remove resources.
They and the batch delete methods accept the objects or their IDs.
Without `force=True`, deleting a test result with steps, or a step with
measurements, fails with `FAILED_PRECONDITION`; with `force=True`, the owned
children are deleted too. A step that has child steps cannot be deleted.

The client wraps every method of the V2 low-level client:

- `remove_condition` removes a condition from a step.
- `add_test_result_metadata`, `remove_test_result_metadata`,
  `add_measurement_metadata`, and `remove_measurement_metadata` link or unlink
  software items, hardware items, and test adapters after creation. A
  measurement can only link items that are linked to its test result, and each
  measurement keeps its own selection. Linking an item to a test result does not
  link it to the test result's measurements. An item cannot be unlinked from a
  test result while a measurement of that test result still references it;
  unlink it from those measurements first.
- `create_measurement` accepts `upper_limit` and `lower_limit` of any supported
  value type. The service stores the limits as given and does not compare them
  with the value. `read_measurement_values` returns the value and both limits;
  select fields with `MeasurementValueField`. `read_measurement_value` and
  `read_measurement_values` accept a `Measurement` or its ID.
- `batch_create_*`, `batch_update_*`, and `batch_delete_*` handle many test
  results, steps, or measurements in one atomic call. Batch updates take a
  dictionary of fields keyed by ID, or a list of builders and objects. Batch
  deletes accept one `force` flag or one flag per ID.
- `TestResult.steps`, `Step.children`, and `Step.measurements` create a whole
  tree in one call. Metadata objects such as `Operator` or `SoftwareItem` can be
  passed instead of IDs to find or create them.
- `create_measurement` accepts `SoftwareItem`, `HardwareItem`, and
  `TestAdapter` objects for inline find-or-create, in addition to their IDs.
- `query_*` methods return `QueryResults`, a list with a `next_page_token` attribute
  that is set when the service has more results.
- JSON values and conditions accept a plain dictionary, or `JsonValue` when the
  value needs attributes. Reads return a `JsonValue` only when attributes are
  present.

## Service behavior and constraints

- V2 create and update methods accept `hightime.datetime` timestamps and
  `hightime.timedelta` durations, converted with the NI precision converters.
  Timestamps must use `datetime.timezone.utc`; other time zones are rejected.
  Round trips are exact to about 1 ns; finer precision is not preserved.
- Test results and steps accept `keywords`, and test results accept `uut_id`
  updates. Those Stage 2 fields are stored once the service delivers the New
  Resource Fields feature. Measurements accept their own optional classification
  `keywords` on create and read.
- Measurement values are converted to scalar, vector, supported NI
  waveform-family, or JSON values; `read_measurement_value` converts them back to
  Python or nitypes values. The `MeasurementValue` type lists the values that can
  be written, and `MeasurementReadValue` lists the values that can be read. A
  single value is always read back as a `Scalar`,
  with or without units, and a list of values as a `Vector`. When a `Scalar` is
  given and `units` is not, the measurement's `units` are taken from the
  `Scalar`. Conditions accept scalar or JSON values. A scalar condition value
  reads back as a plain Python value, or as a `Scalar` when it has extended
  properties other than units. JSON values
  require the service's Stage 3 Structured JSON Storage And Query Support.
- Software item, hardware item, and test adapter IDs on a measurement must first
  be linked to its test result; pass them to `create_test_result`.
- Arguments that take several strings, such as `keywords`, item IDs,
  `read_fields`, and the IDs passed to batch deletes, raise `TypeError` when
  given a single string. Pass a list, for example `keywords=["smoke"]`, so a
  string is not split into its characters.
- Discovery, channel configuration, and cleanup are delegated to the low-level
  V2 client. Its gRPC transport exceptions pass through unchanged; invalid
  wrapper values and update fields fail locally with `TypeError` or
  `ValueError`. Calling a method after `close()` raises `RuntimeError`.
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
