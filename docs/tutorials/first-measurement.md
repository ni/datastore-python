# Your first V2 measurement

This tutorial creates a test execution, records a setup Condition and a
measurement with limits, then reads the value back. It uses the V2 Data Store
client and one scalar reading to show the core workflow.

Before starting, install the Python package and ensure that NI Measurement
Data Services is available in V2 mode. See
[Install and connect](../how-to/install.md).

## Create the test execution

A TestResult represents this run. A Step describes the operation in which the
reading is taken. Add a Condition for the load, then create a Measurement for
the voltage and its acceptance limits:

```python
from nitypes.scalar import Scalar

from ni.datastore.data.v2 import Condition, DataStoreClient, StepField

with DataStoreClient() as client:
    test_result = client.create_test_result("Power supply verification")
    step = client.create_step("Verify 5 V output", test_result_id=test_result.id)
    client.add_condition(step.id, Condition("Load", 1.0, units="A"))

    measurement = client.create_measurement(
        "Output voltage",
        Scalar(5.02, "V"),
        step.id,
        lower_limit=Scalar(4.75, "V"),
        upper_limit=Scalar(5.25, "V"),
    )

    value = client.read_measurement_value(measurement.id, Scalar)
    saved_step = client.get_step(step.id, read_fields=[StepField.CONDITIONS])
    print(value)
    print(saved_step.conditions)
```

The TestResult and Step are created in the V2 Data Store, which returns their
IDs. The Condition belongs to the Step, so it provides context for Measurements
made during that operation. Reading the Measurement value returns a `Scalar`
with its value and units. Limits are stored with the Measurement; your test
system is responsible for evaluating the result and setting an outcome. The
`with` block closes the client when the work is finished.

## Continue learning

* Read [MDS concepts](../concepts/data-model.md) for the model behind these
  resources.
* Use the :doc:`how-to guides <../how-to/index>` for installation, measurement
  value choices, and queries.
* Explore :doc:`runnable V2 notebooks <../examples/index>` for waveforms, batch
  operations, metadata, structured extensions, and updates.
