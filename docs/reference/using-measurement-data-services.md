# Using Measurement Data Services

The NI Measurement Data Services provide a comprehensive solution for storing, organizing, and querying test data and metadata. This document explains the typical workflow for using these services, from initial setup through data analysis.

**Services Overview:**
- **MetadataStoreService** - Manages test context metadata (who, what, where, how)
- **DataStoreService** - Stores and retrieves measurement data and test execution results

## **Complete Workflow Overview**

The typical measurement data workflow follows this sequence:

1. **[Setup Phase](#setup-phase)** - Register metadata entities and schemas
2. **[Test Execution Phase](#test-execution-phase)** - Create test sessions and publish data  
3. **[Analysis Phase](#analysis-phase)** - Query and analyze results

**Workflow Flow:**
```
Setup Phase → Test Execution Phase → Analysis Phase
```

- **Setup Phase**: Create metadata entities (operators, equipment, UUTs), register schemas, set up aliases
- **Test Execution Phase**: Create TestResults, organize into Steps, publish Measurements and Conditions  
- **Analysis Phase**: Query data using OData, perform cross-analysis with metadata context

---

## **Setup Phase**

Before running tests, establish the metadata foundation that describes your test environment and processes.

### **1. Create Core Metadata Entities**

Start by creating the fundamental metadata entities that will be referenced throughout your testing:

#### **Operators**
Register the people who will be running tests:

```python
# Create operators
sarah_id = metadata_store_client.create_operator(Operator(
    operator_name="Sarah Johnson",
    role="Test Engineer",
    extensions={
        "department": "Quality Assurance",
        "certification": "Level 2 Test Technician"
    }
))

mike_id = metadata_store_client.create_operator(Operator(
    operator_name="Mike Chen", 
    role="Senior Technician",
    extensions={
        "department": "Manufacturing",
        "specialization": "RF Testing"
    }
))
```

#### **Test Stations** 
Define the physical locations where testing occurs:

```python
# Create test stations
station_a1_id = metadata_store_client.create_test_station(TestStation(
    test_station_name="Station_A1",
    asset_identifier="STA-001",
    extensions={
        "location": "Building A, Floor 1",
        "station_type": "Production Line"
    }
))

rf_lab_id = metadata_store_client.create_test_station(TestStation(
    test_station_name="RF_Lab_Bench_1",
    asset_identifier="RFL-001", 
    extensions={
        "location": "R&D Lab, Building B",
        "station_type": "Development"
    }
))
```

#### **Hardware Items**
Register test equipment and instruments:

```python
# Create hardware items (test equipment)
dmm_id = metadata_store_client.create_hardware_item(HardwareItem(
    manufacturer="NI",
    model="PXIe-4081",
    serial_number="DMM-001",
    part_number="781061-01",
    calibration_due_date="2025-06-15",
    extensions={
        "accuracy": "7.5 digits",
        "asset_tag": "NI-DMM-001"
    }
))

scope_id = metadata_store_client.create_hardware_item(HardwareItem(
    manufacturer="NI", 
    model="PXIe-5171",
    serial_number="SCOPE-001",
    part_number="783513-01",
    calibration_due_date="2025-08-20",
    extensions={
        "bandwidth": "1 GHz", 
        "sample_rate": "1.25 GS/s"
    }
))
```

#### **Software Items**
Document the software environment:

```python
# Create software items
python_id = metadata_store_client.create_software_item(SoftwareItem(
    product="Python",
    version="3.11.5"
))

nidaqmx_id = metadata_store_client.create_software_item(SoftwareItem(
    product="NI-DAQmx", 
    version="23.3.0"
))

custom_app_id = metadata_store_client.create_software_item(SoftwareItem(
    product="PowerSupply Test Suite",
    version="v2.1.4",
    extensions={
        "build_date": "2024-09-15",
        "git_commit": "a1b2c3d4"
    }
))
```

### **2. Define Products Under Test**

Create UUT definitions and instances:

#### **UUT (Product Definitions)**
```python
# Define the product being tested
power_supply_uut_id = metadata_store_client.create_uut(UUT(
    model_name="PowerSupply v2.1",
    family="Power",
    manufacturers=["ACME Corp"],
    part_number="PS-v2.1-001",
    extensions={
        "max_output": "24V, 10A",
        "efficiency": ">90%"
    }
))
```

#### **UUT Instances (Physical Devices)**
```python
# Create specific device instances
uut_instance_id = metadata_store_client.create_uut_instance(UUTInstance(
    uut_id=power_supply_uut_id,
    serial_number="PS-2024-001456",
    manufacture_date="2024-10-01",
    extensions={
        "lot_number": "L2024-Q4-001",
        "assembly_line": "Line 3"
    }
))
```

### **3. Define Test Procedures**

Create test specifications and procedures:

#### **Test Descriptions**
```python
# Create comprehensive test suites
power_test_desc_id = metadata_store_client.create_test_description(TestDescription(
    uut_id=power_supply_uut_id,
    test_description_name="Power Supply Validation Suite",
    extensions={
        "version": "v2.1",
        "compliance": "IEC 62368-1"
    }
))
```

#### **Individual Tests**
```python
# Create specific test procedures
voltage_test_id = metadata_store_client.create_test(Test(
    test_name="DC Voltage Accuracy Test",
    description="Measures DC voltage accuracy across 5V, 12V, and 24V outputs",
    extensions={
        "test_limits": "±0.1% of reading",
        "test_duration": "~5 minutes"
    }
))

load_test_id = metadata_store_client.create_test(Test(
    test_name="Load Regulation Test", 
    description="Tests voltage stability under varying load conditions",
    extensions={
        "load_range": "0% to 100% rated current",
        "regulation_limit": "±0.5%"
    }
))
```

### **4. Register Extension Schemas** *(Optional)*

Define validation schemas for custom extension fields:

```python
# Register a schema for power supply testing
power_supply_schema = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "hardware_item": {
      "type": "object", 
      "properties": {
        "asset_tag": {"type": "string"},
        "calibration_cert": {"type": "string"},
        "bandwidth": {"type": "string"}
      },
      "required": ["asset_tag"]
    }
  }
}
"""

schema_id = metadata_store_client.register_schema(power_supply_schema)
```

### **5. Create Aliases** *(Optional)*

Set up human-readable names for frequently used entities:

```python
# Create aliases for easy reference
metadata_store_client.create_alias(Alias(
    alias_name="Primary_DMM",
    target_type=AliasTargetType.HARDWARE_ITEM,
    target_id=dmm_id
))

metadata_store_client.create_alias(Alias(
    alias_name="Lead_Test_Engineer", 
    target_type=AliasTargetType.OPERATOR,
    target_id=sarah_id
))

metadata_store_client.create_alias(Alias(
    alias_name="Current_PowerSupply_Design",
    target_type=AliasTargetType.UUT, 
    target_id=power_supply_uut_id
))
```

---

## **Test Execution Phase**

With metadata established, execute tests and publish measurement data.

### **1. Create Test Result Session**

Start each test session by creating a **TestResult**:

```python
# Create a test result for this test session
test_result_id = data_store_client.create_test_result(TestResult(
    uut_instance_id=uut_instance_id,
    operator_id=sarah_id,  # or use alias: "Lead_Test_Engineer"
    test_station_id=station_a1_id,
    test_description_id=power_test_desc_id,
    software_item_ids=[python_id, nidaqmx_id, custom_app_id],
    hardware_item_ids=[dmm_id, scope_id],  # or use aliases
    test_result_name="PowerSupply PS-2024-001456 Validation",
    extensions={
        "test_operator_notes": "First production unit validation",
        "ambient_temperature": "23°C"
    }
))
```

### **2. Create Test Steps**

Organize measurements into logical **Steps**:

```python
# Create test steps within the test result
voltage_step_id = data_store_client.create_step(Step(
    test_result_id=test_result_id,
    test_id=voltage_test_id,
    step_name="DC Voltage Accuracy Check",
    step_type="Measurement",
    notes="Testing 5V, 12V, and 24V outputs under no load"
))

load_step_id = data_store_client.create_step(Step(
    test_result_id=test_result_id, 
    test_id=load_test_id,
    step_name="Load Regulation Test",
    step_type="Measurement", 
    notes="Variable load from 0% to 100% rated current"
))
```

### **3. Publish Test Conditions**

Record environmental and setup conditions during testing:

```python
# Publish conditions (environmental/setup parameters)
data_store_client.publish_condition(
    condition_name="Supply Voltage",
    type="Input Parameter", 
    value=120.0,  # 120V AC input
    step_id=voltage_step_id
)

data_store_client.publish_condition(
    condition_name="Temperature",
    type="Environment",
    value=23.5,  # °C
    step_id=voltage_step_id
)

data_store_client.publish_condition(
    condition_name="Humidity", 
    type="Environment",
    value=45.2,  # %RH
    step_id=voltage_step_id
)
```

### **4. Publish Measurements**

Capture actual measurement data:

#### **Single Measurements**
```python
# Publish individual measurements
published_measurement = data_store_client.publish_measurement(
    measurement_name="5V Output Voltage",
    value=5.023,  # Measured 5.023V
    timestamp=datetime.now(),
    outcome=Outcome.OUTCOME_PASSED,
    step_id=voltage_step_id,
    hardware_item_ids=[dmm_id],
    notes="DMM reading at no load"
)
```

#### **Waveform Measurements**  
```python
# Publish complex data (waveforms, spectra, etc.)
waveform_data = AnalogWaveform(
    samples=[1.0, 2.0, 3.0, 2.0, 1.0, 0.0, -1.0],
    sample_interval=1e-6,  # 1 µs per sample
    start_time=0.0
)

data_store_client.publish_measurement(
    measurement_name="Output Ripple Waveform",
    value=waveform_data,
    timestamp=datetime.now(),
    outcome=Outcome.OUTCOME_PASSED,
    step_id=voltage_step_id, 
    hardware_item_ids=[scope_id],
    notes="Ripple measurement at full load"
)
```

#### **Batch Measurements** *(For Parametric Sweeps)*
```python
# Publish multiple related measurements efficiently
load_currents = [0.0, 2.5, 5.0, 7.5, 10.0]  # Load current sweep
output_voltages = [5.025, 5.023, 5.021, 5.019, 5.018]  # Corresponding voltages

data_store_client.publish_measurement_batch(
    measurement_name="Load Regulation Sweep",
    values=output_voltages,
    timestamps=[datetime.now()] * len(output_voltages),
    outcomes=[Outcome.OUTCOME_PASSED] * len(output_voltages),
    step_id=load_step_id,
    hardware_item_ids=[dmm_id]
)

# Publish corresponding load conditions
data_store_client.publish_condition_batch(
    condition_name="Load Current", 
    type="Test Parameter",
    values=load_currents,
    step_id=load_step_id
)
```

### **5. Update Test Results**

Mark test completion and overall outcome:

```python
# Update test result with final outcome
test_result = data_store_client.get_test_result(test_result_id)
test_result.end_date_time = datetime.now()
test_result.outcome = Outcome.OUTCOME_PASSED

# The test result is automatically updated when retrieved again
```

---

## **Analysis Phase**

Query and analyze the stored measurement data and metadata.

### **1. Query Measurements**

Use OData queries to find and filter measurement data:

#### **Basic Queries**
```python
# Find all measurements from a specific test result
measurements = data_store_client.query_measurements(
    f"$filter=test_result_id eq '{test_result_id}'"
)

# Find failed measurements
failed_measurements = data_store_client.query_measurements(
    "$filter=outcome eq 'OUTCOME_FAILED'"
)

# Find measurements by name
voltage_measurements = data_store_client.query_measurements(
    "$filter=contains(measurement_name, 'Voltage')"
)
```

#### **Complex Queries**
```python
# Find measurements from specific equipment that failed
equipment_failures = data_store_client.query_measurements(
    f"$filter=outcome eq 'OUTCOME_FAILED' and contains(hardware_item_ids, '{dmm_id}')"
)

# Find recent measurements
recent_measurements = data_store_client.query_measurements(
    "$filter=start_date_time gt 2024-10-01T00:00:00Z&$orderby=start_date_time desc"
)

# Find measurements from specific operator
operator_measurements = data_store_client.query_measurements(
    f"$filter=contains(test_result_id, '{test_result_id}') and operator_id eq '{sarah_id}'"
)
```

### **2. Query Test Context**

Analyze test metadata to understand patterns:

#### **Test Results Analysis**
```python
# Find all test results for a UUT model
test_results = data_store_client.query_steps(
    f"$filter=contains(test_result_id, '{test_result_id}')"
)

# Find tests by operator
sarah_tests = metadata_store_client.query_operators(
    "$filter=operator_name eq 'Sarah Johnson'"
)
```

#### **Equipment Usage Tracking**
```python
# Find all hardware items due for calibration
equipment_due = metadata_store_client.query_hardware_items(
    "$filter=calibration_due_date lt '2024-12-31'"
)

# Find measurements using specific equipment
equipment_usage = data_store_client.query_measurements(
    f"$filter=contains(hardware_item_ids, '{scope_id}')"
)
```

### **3. Retrieve Measurement Data**

Access the actual measured values:

```python
# Get measurement data using moniker
for measurement in measurements:
    if measurement.data_type == "Scalar":
        value = data_store_client.read_data(measurement, expected_type=float)
        print(f"{measurement.measurement_name}: {value}")
    elif measurement.data_type == "AnalogWaveform":
        waveform = data_store_client.read_data(measurement, expected_type=AnalogWaveform)
        print(f"{measurement.measurement_name}: {len(waveform.samples)} samples")
```

### **4. Cross-Reference with Metadata**

Combine measurement data with metadata for comprehensive analysis:

```python
# Analyze test results with full context
for measurement in measurements:
    # Get associated metadata
    test_result = data_store_client.get_test_result(measurement.test_result_id)
    step = data_store_client.get_step(measurement.step_id)
    
    # Get UUT instance and model info
    uut_instance = metadata_store_client.get_uut_instance(test_result.uut_instance_id)
    uut = metadata_store_client.get_uut(uut_instance.uut_id)
    
    # Get operator info
    operator = metadata_store_client.get_operator(test_result.operator_id)
    
    # Get equipment info
    hardware_items = [
        metadata_store_client.get_hardware_item(hw_id) 
        for hw_id in measurement.hardware_item_ids
    ]
    
    print(f"Measurement: {measurement.measurement_name}")
    print(f"  UUT: {uut.model_name} S/N: {uut_instance.serial_number}")
    print(f"  Operator: {operator.operator_name} ({operator.role})")
    print(f"  Equipment: {[hw.model for hw in hardware_items]}")
    print(f"  Outcome: {measurement.outcome}")
```

### **5. Advanced Analysis Examples**

#### **Trend Analysis**
```python
# Track performance over time for a UUT model
uut_instances = metadata_store_client.query_uut_instances(
    f"$filter=uut_id eq '{power_supply_uut_id}'"
)

for instance in uut_instances:
    measurements = data_store_client.query_measurements(
        f"$filter=contains(test_result_id, '{instance.uut_instance_id}') and measurement_name eq '5V Output Voltage'"
    )
    # Analyze voltage accuracy trends...
```

#### **Equipment Performance Analysis**
```python
# Analyze calibration impact on measurements
pre_cal_measurements = data_store_client.query_measurements(
    f"$filter=contains(hardware_item_ids, '{dmm_id}') and start_date_time lt '2024-06-15'"
)

post_cal_measurements = data_store_client.query_measurements(
    f"$filter=contains(hardware_item_ids, '{dmm_id}') and start_date_time gt '2024-06-15'"
)
# Compare measurement accuracy before/after calibration...
```

#### **Operator Performance Comparison**
```python
# Compare test results between operators
for operator_id in [sarah_id, mike_id]:
    operator = metadata_store_client.get_operator(operator_id)
    measurements = data_store_client.query_measurements(
        f"$filter=operator_id eq '{operator_id}' and outcome eq 'OUTCOME_FAILED'"
    )
    failure_rate = len(measurements) / total_measurements_by_operator[operator_id] * 100
    print(f"{operator.operator_name}: {failure_rate:.1f}% failure rate")
```

---

## **Best Practices**

### **Metadata Management**
- **Create aliases** for frequently referenced entities
- **Use extension schemas** to enforce data consistency
- **Register metadata entities once** and reuse across multiple tests
- **Keep calibration dates current** for traceability

### **Test Execution**
- **Always create a TestResult** before publishing measurements
- **Group related measurements** into logical Steps
- **Include environmental conditions** that might affect results
- **Use batch operations** for parametric sweeps to improve performance

### **Data Organization**
- **Use consistent naming conventions** for measurements and steps
- **Include meaningful notes** and descriptions
- **Associate measurements with relevant hardware/software** for traceability
- **Set appropriate outcomes** (PASSED/FAILED/INDETERMINATE) for analysis

### **Querying and Analysis**
- **Use specific OData filters** to reduce query response size
- **Combine metadata and measurement queries** for comprehensive analysis
- **Cache frequently accessed metadata** entities
- **Use measurement names and types** to group related data

---

## **Integration Patterns**

### **Automated Test Systems**
```python
class TestAutomation:
    def __init__(self):
        self.metadata_client = MetadataStoreClient()
        self.data_client = DataStoreClient()
        
    def run_automated_test(self, uut_serial: str):
        # 1. Look up UUT instance by serial number
        instances = self.metadata_client.query_uut_instances(
            f"$filter=serial_number eq '{uut_serial}'"
        )
        
        # 2. Create test result
        test_result_id = self.data_client.create_test_result(...)
        
        # 3. Execute test steps
        for test_step in self.test_sequence:
            step_id = self.data_client.create_step(...)
            self.execute_step(step_id, test_step)
            
        # 4. Determine overall result
        self.finalize_test_result(test_result_id)
```

### **Batch Processing**
```python
def process_test_batch(uut_serials: List[str]):
    """Process multiple UUTs efficiently."""
    
    # Create all test results first
    test_result_ids = []
    for serial in uut_serials:
        test_result_id = data_store_client.create_test_result(...)
        test_result_ids.append(test_result_id)
    
    # Execute tests in parallel/batch
    for test_result_id in test_result_ids:
        execute_test_sequence(test_result_id)
        
    # Analyze results
    analyze_batch_results(test_result_ids)
```

This comprehensive workflow ensures full traceability, enables powerful analysis capabilities, and maintains data integrity across your entire test ecosystem.
