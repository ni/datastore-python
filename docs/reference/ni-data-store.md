# NI Data Store

The NI Data Store provides a structured way to store and organize test data. It consists of several core entities that work together to capture the complete picture of test execution, from high-level test sessions down to individual measurements and environmental conditions.

## **Core Entities**

### **TestResult** 
A **TestResult** represents a complete test session or test execution run for a specific Unit Under Test (UUT). It's the top-level container that captures everything that happened when you tested a particular device.

**Fields:**
- `id` (string) - Unique identifier (GUID)
- `uut_instance_id` (string) - ID of the Unit Under Test instance
- `operator_id` (string) - ID of the operator who ran the test
- `test_station_id` (string) - ID of the test station used
- `test_description_id` (string) - ID of the test description/specification
- `software_item_ids` (list of strings) - IDs of software used during testing
- `hardware_item_ids` (list of strings) - IDs of hardware used during testing  
- `test_adapter_ids` (list of strings) - IDs of test adapters used
- `name` (string) - Human-readable name for the test run
- `start_date_time` (timestamp) - When the test execution started
- `end_date_time` (timestamp) - When the test execution finished
- `outcome` (enum) - Overall test result (PASSED, FAILED, INDETERMINATE, UNSPECIFIED)
- `link` (string) - Optional link to additional resources
- `extension` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation
- `error_information` (ErrorInformation) - Error details if test result failed

**Real-world example**: When you put a circuit board on a test station and run a complete validation sequence, that entire session becomes one TestResult. It includes metadata like who ran the test, when it was run, what test station was used, and links to all the measurements and steps that were performed.

### **Step**
A **Step** represents an individual test procedure or operation within a larger test sequence. Each step typically tests a specific aspect or function of the UUT and serves as a container for related measurements and conditions.

**Fields:**
- `id` (string) - Unique identifier (GUID) 
- `parent_step_id` (string) - ID of parent step (for hierarchical steps)
- `test_result_id` (string) - ID of the associated TestResult
- `test_id` (string) - ID of the test definition/specification
- `name` (string) - Human-readable name for the step
- `step_type` (string) - Type/category of the step
- `notes` (string) - Additional notes about the step
- `start_date_time` (timestamp) - When the step started executing
- `end_date_time` (timestamp) - When the step finished executing
- `outcome` (enum) - Result of this step (PASSED, FAILED, INDETERMINATE, UNSPECIFIED)
- `link` (string) - Optional link to additional resources
- `extension` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation
- `error_information` (ErrorInformation) - Error details if step failed

**Real-world examples**:
- "Measure DC Voltage on Pin 5" 
- "Verify Communication Protocol Response"
- "Check LED Brightness at 100mA"
- "Functional Test - Power On Sequence"
- "Calibration - Set Reference Voltage"

Each step belongs to a TestResult and can contain multiple measurements and conditions.

### **PublishedMeasurement**
A **PublishedMeasurement** represents actual measurement data captured during a test step. This is the core data entity that stores the measured values, whether they are simple scalars, complex waveforms, or other data types.

**Fields:**
- `moniker` (Moniker) - Data location identifier for retrieving the actual measurement values
- `published_conditions` (list) - Environmental conditions present during measurement
- `id` (string) - Unique identifier for this measurement
- `test_result_id` (string) - ID of the associated TestResult
- `step_id` (string) - ID of the associated Step
- `software_item_ids` (list of strings) - Software used to capture this measurement
- `hardware_item_ids` (list of strings) - Hardware used to capture this measurement
- `test_adapter_ids` (list of strings) - Test adapters used to capture this measurement
- `name` (string) - Name used to group related measurements
- `value_type` (string) - Type of data (e.g., "Scalar", "AnalogWaveform", "Spectrum")
- `notes` (string) - Additional notes about the measurement
- `start_date_time` (timestamp) - When measurement capture started
- `end_date_time` (timestamp) - When measurement capture finished
- `outcome` (enum) - Result of this measurement (PASSED, FAILED, INDETERMINATE, UNSPECIFIED)
- `parametric_index` (int) - Index within parametric set, or -1 for entire set
- `error_information` (ErrorInformation) - Error details if measurement failed

**Supported Data Types:**
- **Scalar** - Single float, int, str or boolean values
- **Vector** - Arrays of float, int, str or boolean values
- **DoubleAnalogWaveform** - Analog waveform with double precision
- **DoubleXYData** - XY coordinate data with double precision
- **I16AnalogWaveform** - Analog waveform with 16-bit integer precision
- **DoubleComplexWaveform** - Complex waveform with double precision
- **I16ComplexWaveform** - Complex waveform with 16-bit integer precision
- **DoubleSpectrum** - Frequency spectrum data with double precision
- **DigitalWaveform** - Digital waveform data

**Real-world examples**:
- A voltage reading: `3.297V` from a multimeter
- A waveform: Time-series data from an oscilloscope showing a signal over time
- A frequency measurement: `1.0234 MHz` from a frequency counter  
- A boolean result: `PASS/FAIL` from a functional test
- An array of values: Temperature readings over time from a thermal sensor

### **PublishedCondition**
A **PublishedCondition** represents environmental or contextual information that was present during test execution. Conditions capture the state of the test environment, input parameters, or other contextual data that might affect measurement results.

**Fields:**
- `moniker` (Moniker) - Data location identifier for retrieving the condition value
- `id` (string) - Unique identifier for this condition
- `name` (string) - Name of the condition (e.g., "Temperature", "Supply Voltage")
- `condition_type` (string) - Type/category of the condition (e.g., "Environment", "Input Parameter")
- `step_id` (string) - ID of the associated Step
- `test_result_id` (string) - ID of the associated TestResult

**Real-world examples**:
- Environmental conditions: Temperature = 23.5°C, Humidity = 45%
- Input parameters: Supply Voltage = 5.0V, Input Frequency = 1kHz  
- Test configuration: Gain Setting = "High", Filter = "Low Pass"
- Calibration data: Reference Standard = "NIST-123", Cal Date = "2024-01-15"

### **Supporting Types**

#### **Outcome Enum**
Represents the result of a test or measurement:
- `UNSPECIFIED` - The outcome is not specified or unknown
- `PASSED` - The measurement or test passed successfully
- `FAILED` - The measurement or test failed
- `INDETERMINATE` - The measurement or test result is indeterminate or inconclusive

#### **ErrorInformation**
Contains error details when operations fail:
- `error_code` (int) - Numeric error code
- `message` (string) - Human-readable error message
- `source` (string) - Source/origin of the error

## **The Hierarchy**
```
TestResult (Test session for Serial# ABC123)
├── Step 1: "Power Supply Verification"
│   ├── PublishedMeasurement: "5V Rail Voltage" = 5.02V
│   ├── PublishedMeasurement: "Current Draw" = 245mA
│   └── PublishedCondition: "Temperature" = 23.5°C
├── Step 2: "Digital I/O Test"  
│   ├── PublishedMeasurement: "Pin 1 High Level" = 3.28V
│   └── PublishedMeasurement: "Pin 2 Response Time" = 150μs
└── Step 3: "Communication Test"
    └── PublishedMeasurement: "UART Data Rate" = 115200 bps
```

This hierarchical structure allows you to:
- **Organize data logically** - Group related measurements by test step
- **Drill down progressively** - From test sessions → steps → individual measurements
- **Track context** - Associate environmental conditions with specific measurements
- **Enable powerful queries** - Search and filter data at any level of the hierarchy
- **Maintain traceability** - Link every measurement back to its test context

## **Data Access Patterns**

The NI Data Store supports two primary data access patterns:

1. **Publishing Data** - Store test results, steps, measurements, and conditions during test execution
2. **Querying Data** - Retrieve and analyze test data using OData query syntax

All entities support OData queries for flexible data retrieval and analysis.