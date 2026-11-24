# Choose and record a measurement value

Use the value representation that preserves the physical meaning and analysis
needs of an observation. All of these value shapes are stored as a V2
Measurement under a Step.

| Observation | Suitable value |
|---|---|
| One voltage reading | `Scalar`, with units such as `V` |
| A list of repeated readings | `Vector` |
| X and Y values that form a curve | `XYData` |
| Samples indexed over time | `AnalogWaveform`, `DigitalWaveform`, or `ComplexWaveform` |
| Frequency-domain samples | `Spectrum` |
| Structured application data | A dictionary or `JsonValue` |

For example, use a `Scalar` for one measured output and a waveform when the
signal shape over time matters:

```python
import numpy as np
from nitypes.scalar import Scalar
from nitypes.waveform import AnalogWaveform, SampleIntervalMode, Timing
import hightime as ht

from ni.datastore.data.v2 import DataStoreClient

with DataStoreClient() as client:
    test_result = client.create_test_result("Power supply verification")
    step = client.create_step("Verify output", test_result_id=test_result.id)
    voltage = client.create_measurement(
        "Output voltage",
        Scalar(5.02, "V"),
        step.id,
    )
    ripple = AnalogWaveform(
        sample_count=3,
        raw_data=np.array([0.01, -0.02, 0.01]),
        timing=Timing(SampleIntervalMode.NONE, time_offset=ht.timedelta()),
    )
    waveform = client.create_measurement("Output ripple", ripple, step.id)
```

The Step groups both observations under the same test execution. See
[Your first V2 measurement](../tutorials/first-measurement.md) for an
introduction to creating and reading a scalar Measurement.

## Keep conditions with the step

Conditions describe the setup or environment shared by the work in a Step:

```python
from ni.datastore.data.v2 import Condition, DataStoreClient

with DataStoreClient() as client:
    test_result = client.create_test_result("Power supply verification")
    step = client.create_step("Verify output", test_result_id=test_result.id)
    client.add_condition(step.id, Condition("Load", 1.0, units="A"))
```

If the setup changes between observations, use Steps that preserve the
distinction—for example, one Step for each load point in a sweep. If a sequence
or relationship is itself the result, represent it as a vector, XY dataset, or
waveform as appropriate.

## Store limits and outcomes

`lower_limit` and `upper_limit` can be stored with a Measurement. The service
stores the supplied limits but does not compare them with the value. Your test
application evaluates the result and records the relevant outcome.

The `measurement value notebook <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/measurement-values/measurement_values.ipynb>`_
shows additional supported value types and limits.
