# Understanding Measurement Data Services

The NI Measurement Data Services provide a comprehensive solution for storing, organizing, and querying test data and metadata. This document explains the typical workflow for using these services, from initial setup through data analysis.

This page introduces the concepts behind Measurement Data Services (MDS) and how they fit together. It focuses on the V2 Data Store model, where test results, steps, measurements, and conditions form a structured record of test execution. It is intended as a conceptual starting point; see the [V2 Python API reference](ni-data-store-v2.md) and [workflow guide](using-measurement-data-services.md) for implementation details and examples.

## The basic idea

An instrument produces data, but the data is most useful when it can be understood later: what was tested, how it was tested, what the test setup was, what was observed, and whether the observation met the test's criteria. MDS stores measurements together with this context in a queryable structure instead of leaving results as disconnected numbers, files, or logs.

The V2 Data Store organizes a test execution as a hierarchy:

```text
TestResult: validation of power supply PS-1042
├── Step: verify the 5 V output
│   ├── Conditions: input voltage = 120 V, load = 1 A
│   ├── Measurement: output voltage = 5.02 V
│   └── Measurement: output ripple = waveform
└── Step: verify the 12 V output
    ├── Conditions: input voltage = 120 V, load = 1 A
    └── Measurement: output voltage = 12.01 V
```

In this model, a **TestResult** represents one execution, a **Step** groups the work performed as part of that execution, and each step owns its **Measurements** and **Conditions**. Steps can be nested to represent a test plan or procedure with meaningful levels of detail.

## The entities

### TestResult: one execution

A TestResult is the record of one run of a test process. It answers questions such as:

- Which unit under test (UUT) was tested?
- When did the run start and finish?
- Who ran it, and at which test station?
- Which test description, software, hardware, and adapters were involved?
- What was the overall status and outcome?

For example, testing serial-number PS-1042 on a particular bench in a production station is one TestResult. Running the same procedure on PS-1043 creates another TestResult, even if both executions use the same test definition and equipment.

The TestResult provides the execution-level context. Its steps contain the detailed work and observations. Metadata such as the UUT, operator, and station can be linked to the TestResult so results can later be searched or interpreted in context.

### Step: a meaningful part of the execution

A Step is an operation or stage within a TestResult. A step might represent a test case, a setup operation, a test sequence, or one measurement point in a procedure. Steps can have child steps, so the hierarchy can match the way a test is actually organized.

For a power-supply validation, a top-level step could be “Verify outputs,” with child steps for the 5 V and 12 V outputs. Each child can record the conditions for that output and the measurements taken there.

The Step is the center of the V2 data model: it groups the observations and the conditions under which they were made. This lets users query or read a step together with its measurements and conditions, rather than treating those records as unrelated items.

### Condition: context for a step

A Condition records a value that describes the test setup or environment, rather than a measured result. Examples include:

- The applied input voltage or current
- Ambient temperature or humidity
- A selected operating mode or configuration
- The load, frequency, or range used for a test

Conditions belong to a Step. In the V2 model they are shared context for that step, not independent per-measurement records. For example, if the input voltage and load are unchanged while the 5 V output and ripple are measured, both measurements belong under the same step conditions. If a condition changes, represent the changed context with a separate step (or another appropriate step in the procedure).

### Measurement: an observation

A Measurement is an observation made during a step. It has a name and a value, and can also record units, limits, timestamps, duration, outcome, notes, and associated equipment or software.

For example, “5 V output” is a measurement with a value of `5.02 V`. “Output ripple” is a different measurement, even when taken during the same step, because it represents a different observation and may have a different kind of value.

The value's shape should reflect what was measured:

- **A single reading** can be a scalar, such as `5.02 V` or `23.4 degC`.
- **A collection of related readings** can be a vector, such as a set of voltage samples or repeated results.
- **A relationship between two arrays** can be XY data, such as measured current versus voltage.
- **A signal over time** can be an analog, digital, or complex waveform.
- **A frequency-domain result** can be a spectrum.
- **Structured application-specific data** can be represented as JSON.

These are different ways to represent observations, not different entity types in the hierarchy. They are all Measurement values. Choose the form that preserves the meaning and context of the result: for instance, store a waveform when the signal shape over time matters, rather than reducing it to a single average.

Limits can be stored alongside a measurement value, but the Data Store records them; it does not decide whether the value passes those limits. The test application or test system determines and records the outcome.

## Example: characterizing a power supply

Suppose a test engineer verifies a power supply at several output settings:

1. Create a TestResult for this run, identifying the unit, test station, operator, and relevant equipment.
2. Create a Step for each test phase or operating point, such as “Verify 5 V output at 1 A.”
3. Add Conditions to the step for the setup, such as input voltage, load, and ambient temperature.
4. Add Measurements for the observations made under those conditions:
   - Output voltage as a scalar with volts as its units and the applicable lower and upper limits.
   - Output ripple as a waveform if its variation over time matters.
   - A sweep as XY data if the result is a relationship between two variables.
5. Record status and outcome for the test execution, steps, or measurements as appropriate.

If the load changes and a new reading is taken at each load, the data can be organized as separate steps with their own load conditions and scalar measurements. If the purpose is to preserve one continuous sweep, that sweep can instead be recorded as one measurement using a value representation that captures the series or relationship. The choice depends on what users need to retrieve and compare later: individual test points, or one combined data set.

This structure makes it possible to retrieve the 5 V result with the input voltage, load, equipment, and test-run context that explain it. Users can query by resource fields and then read the associated measurement values, rather than relying on a filename or an undocumented convention to reconstruct the context.

## Metadata and measurement data

MDS separates **measurement data** from **metadata that describes the testing context**:

- The Data Store holds TestResults, Steps, Conditions, Measurements, and their relationships.
- The Metadata Store manages reusable entities such as UUT definitions and instances, operators, test stations, software, hardware, and test adapters.

The TestResult and Measurement can link to these metadata entities. This avoids repeating a full description of a test station or instrument on every reading, while still allowing users to retrieve measurements with their relevant context.

## From capture to retrieval

The V2 workflow follows the structure of the data:

1. Create a TestResult for a test execution.
2. Create Steps that reflect the procedure or meaningful measurement stages.
3. Record each step's Conditions and Measurements.
4. Query TestResults, Steps, or Measurements to find the data of interest.
5. Read the stored measurement values and interpret them with their step and metadata context.

This model supports both focused queries, such as finding a particular measurement, and analysis across many executions, such as comparing a reading across UUTs, test stations, or time. The [V2 Python API reference](ni-data-store-v2.md) explains the V2 client operations and types. The [workflow guide](using-measurement-data-services.md) provides a longer example of using the Python package.
