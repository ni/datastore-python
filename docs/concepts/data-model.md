# Understanding Measurement Data Services

The NI Measurement Data Services provide a comprehensive solution for storing, organizing, and querying test data and metadata. This document explains the typical workflow for using these services, from initial setup through data analysis.

This page explains the V2 Data Store model: how test results, steps, conditions,
and measurements fit together. For a first hands-on workflow, see the
[first-measurement tutorial](../tutorials/first-measurement.md). For exact
client operations, see the [V2 Python API reference](../reference/ni-data-store-v2.md).

## MDS in a test and measurement workflow

An instrument produces data, but the data is most useful when it can be
understood later: what was tested, how it was tested, what the setup was, what
was observed, and how the observation was evaluated. MDS stores measurement
values together with structured execution context so teams can retrieve and
interpret results without reconstructing meaning from disconnected files,
numbers, or logs.

In the V2 Data Store, the central relationship is:

```text
TestResult: validation of power supply PS-1042
└── Steps
    ├── Step: verify the 5 V output
    │   ├── Conditions: input voltage = 120 V, load = 1 A
    │   ├── Measurement: output voltage = 5.02 V
    │   └── Measurement: output ripple = waveform
    └── Step: verify the 12 V output
        ├── Conditions: input voltage = 120 V, load = 1 A
        └── Measurement: output voltage = 12.01 V
```

A **TestResult** represents one execution. It contains **Steps**, which
organize the operations or stages performed during that execution. Each Step
is the natural center for the **Conditions** under which work was performed
and the **Measurements** observed. Steps can be nested to reflect a procedure,
test plan, or other useful hierarchy.

## TestResult: one execution

A TestResult records one run of a test process. It answers questions such as:

- Which unit under test (UUT) was tested?
- When did the run start and finish?
- Who ran it, and at which test station?
- Which test description, software, hardware, and adapters were involved?
- What was the overall status and outcome?

Testing serial-number PS-1042 on a particular bench is one TestResult. Running
the same procedure on PS-1043 creates another TestResult, even if both
executions use the same test definition and equipment.

The TestResult provides execution-level context. Its Steps hold the detailed
work and observations; links to reusable metadata provide additional context
about the UUT, operator, station, and equipment.

## Step: a meaningful part of the execution

A Step is an operation or stage within a TestResult. It might represent a test
case, setup operation, test sequence, or one measurement point in a procedure.
For example, a top-level “Verify outputs” Step could have child Steps for the
5 V and 12 V outputs.

The Step groups related observations and the Conditions that apply to them.
When the setup changes meaningfully—for example, when the load changes from
1 A to 5 A—use a separate Step when that makes the resulting data easier to
interpret and compare.

## Condition: context for a step

A Condition records a value describing the test setup or environment, rather
than a measured result. Examples include:

- Applied input voltage or current
- Ambient temperature or humidity
- A selected operating mode or configuration
- The load, frequency, or range used for a test

Conditions belong to a Step and provide shared context for its Measurements.
If input voltage and load are unchanged while both output voltage and ripple
are measured, those observations can be grouped under the same Step and
Conditions. Conditions are not independent per-measurement records.

## Measurement: an observation

A Measurement is an observation made during a Step. It has a name and a value,
and can also carry units, limits, timestamps, duration, outcome, notes, and
associated equipment or software.

“5 V output” might be a scalar value of `5.02 V`. “Output ripple” is another
Measurement from the same Step, but its value may be a waveform because the
signal's shape over time matters.

The Measurement value should preserve the meaning of the observation:

| What was observed | Example value shape |
|---|---|
| One reading | Scalar, such as `5.02 V` or `23.4 degC` |
| A sequence of related readings | Vector |
| A relationship between two arrays | XY data, such as current versus voltage |
| A signal over time | Analog, digital, or complex waveform |
| A frequency-domain result | Spectrum |
| Structured application-specific data | JSON |

These are different value representations for the same Measurement entity.
Choose the representation that preserves the information needed for later
analysis—for example, store a waveform when its shape over time matters rather
than reducing it to an average.

Limits can be stored alongside a value, but the Data Store records them; it
does not determine whether the value passes. The test application or test
system evaluates the result and records an outcome.

## Example: characterizing a power supply

Suppose a test engineer verifies a power supply at several output settings:

1. Create a TestResult for this run, identifying the unit, test station,
   operator, and relevant equipment.
2. Create Steps for the test phases or operating points, such as “Verify 5 V
   output at 1 A.”
3. Add Conditions to each Step for the setup, such as input voltage, load, and
   ambient temperature.
4. Add Measurements for the observations made under those Conditions:
   - Output voltage as a scalar with volts as its units and the applicable
     lower and upper limits.
   - Output ripple as a waveform if its variation over time matters.
   - A sweep as XY data if the result is a relationship between two variables.
5. Record status and outcome for the execution, Steps, or Measurements as
   appropriate.

If the load changes and a new reading is taken at each load, the data can be
organized as separate Steps with their own load Conditions and scalar
Measurements. If the purpose is to preserve one continuous sweep, record it as
one Measurement using a value representation that captures the series or
relationship. Choose based on whether users need to retrieve individual test
points or analyze one combined dataset.

The resulting structure lets a user retrieve the 5 V result with the input
voltage, load, equipment, and test-run context that explain it. Users can query
resources and read the associated value instead of relying on filenames or
undocumented conventions to reconstruct context.

## Measurement data and metadata

MDS has separate Data Store and Metadata Store services:

- The **Data Store** holds TestResults, Steps, Conditions, Measurements, and
  their relationships.
- The **Metadata Store** manages reusable entities such as UUT definitions and
  instances, operators, test stations, software, hardware, and test adapters.

TestResults and Measurements can link to these metadata entities. This avoids
repeating a full description of an instrument or test station for every
reading, while allowing results to be retrieved with relevant context. The
Metadata Store API remains a separate client surface; see the
[metadata concepts](../reference/ni-metadata-store.md) and its generated
:doc:`Python API reference <../autoapi/ni/datastore/metadata/index>`.

## From capture to retrieval

The V2 workflow follows the data structure:

1. Create a TestResult for a test execution.
2. Create Steps that reflect the procedure or meaningful measurement stages.
3. Record each Step's Conditions and Measurements.
4. Query TestResults, Steps, or Measurements to find data of interest.
5. Read the stored measurement values and interpret them with their Step and
   metadata context.

This supports both focused queries, such as finding one measurement, and
analysis across executions, such as comparing results across UUTs, test
stations, or time. Continue with the [first-measurement tutorial](../tutorials/first-measurement.md),
or use the [V2 Python API reference](../reference/ni-data-store-v2.md) when you
need exact client operations.
