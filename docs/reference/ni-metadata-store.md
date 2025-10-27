# NI Metadata Store

The NI Metadata Store supports the digital thread weaving together measurement results with metadata that describes **who**, **what**, **where**, and **how** tests are performed. This creates a complete context around your test data, enabling traceability and analysis across your entire test ecosystem.

**Based on:** [`metadata_store.proto`](https://github.com/ni/ni-apis/blob/main/ni/measurements/metadata/v1/metadata_store.proto)

## **Operator**
An **Operator** represents a person who performs tests or operates test equipment. This captures the human element in your test process.

**Fields:**
- `operator_name` (string) - The name of the operator
- `role` (string) - The role of the operator (e.g., "Test Engineer", "Lab Technician")
- `link` (string) - URI to resource describing the operator
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- "Sarah Johnson" - Test Engineer who runs daily production tests
- "Mike Chen" - Senior Technician who performs calibrations  
- "Alex Smith" - Lab Assistant who conducts R&D validation tests

Each operator has a role (e.g., "Test Engineer", "Lab Technician", "Quality Inspector") that helps categorize their responsibilities and skill level.

## **Test Station**
A **Test Station** represents a physical location or setup where testing is performed. This could be a bench, rack, or dedicated test system.

**Fields:**
- `test_station_name` (string) - The name of the test station
- `asset_identifier` (string) - For tracking and inventory purposes
- `link` (string) - URI to resource describing the test station
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- "Station_A1" - Production line station #1 for power supply testing
- "Bench_RF_Lab" - RF laboratory bench with spectrum analyzers
- "Burn_In_Rack_3" - Environmental stress testing chamber
- "Cal_Lab_Station" - Precision calibration workstation with reference standards

Test stations help track where tests were performed, enabling analysis of station-specific issues or performance variations.

## **UUT (Unit Under Test)**
A **UUT** represents a product definition or model being tested. This is the "what" - the type of device or product under test.

**Fields:**
- `model_name` (string) - The name of the UUT model
- `family` (string) - The UUT family or category
- `manufacturers` (list of strings) - List of manufacturers of the UUT
- `part_number` (string) - The part number of the UUT
- `link` (string) - URI to resource describing the UUT
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- Model: "PowerSupply v2.1", Family: "Power" - A specific power supply product
- Model: "Audio Amplifier v1.3", Family: "Audio" - An audio amplifier design
- Model: "RF Transceiver Gen3", Family: "Communications" - A radio frequency module
- Model: "Motor Controller v4.0", Family: "Industrial" - An industrial motor controller

UUTs represent the product designs, while UUT instances represent individual physical devices.

## **UUT Instance**
A **UUT Instance** represents an individual physical device with a unique serial number. This is a specific unit of the UUT model being tested.

**Fields:**
- `uut_id` (string) - The ID of the UUT associated with this instance (GUID or alias)
- `serial_number` (string) - The serial number of the UUT instance
- `asset_identifier` (string) - For tracking and inventory purposes
- `manufacture_date` (string) - When the instance was manufactured
- `link` (string) - URI to resource describing the UUT instance
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- UUT: "PowerSupply v2.1", Serial: "PS-2024-001" - First power supply unit built in 2024
- UUT: "Audio Amplifier v1.3", Serial: "AMP-2024-456" - Specific amplifier with serial number
- UUT: "RF Transceiver Gen3", Serial: "RF-X7G9-2024-789" - Individual transceiver unit

Each UUT instance tracks the test history for that specific physical device throughout its lifecycle.

## **Hardware Item**
A **Hardware Item** represents test equipment, instruments, or tools used during testing. This captures what physical equipment was involved in generating the measurements.

**Fields:**
- `manufacturer` (string) - The vendor of the hardware item
- `model` (string) - The name/model number of the hardware item
- `serial_number` (string) - Unique serial number for tracking
- `part_number` (string) - Manufacturer's part number
- `asset_identifier` (string) - For tracking and inventory purposes
- `calibration_due_date` (string) - When calibration expires
- `link` (string) - URI to resource describing the hardware item
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- Manufacturer: "NI", Model: "PXIe-4081", Serial: "DMM001" - Digital multimeter
- Manufacturer: "Keysight", Model: "E5071C", Serial: "VNA789" - Vector network analyzer  
- Manufacturer: "Tektronix", Model: "MSO64", Serial: "SCOPE456" - Mixed-signal oscilloscope
- Manufacturer: "Fluke", Model: "8588A", Serial: "REF123" - Reference multimeter

Hardware items include calibration information and help ensure measurement traceability.

## **Software Item**
A **Software Item** represents software tools, environments, or versions used during testing. This captures the software context that could affect test results.

**Fields:**
- `product` (string) - The software product name (letters, numbers, spaces, hyphens, underscores, parentheses, periods; must begin and end with letter or number)
- `version` (string) - The version of the software item
- `link` (string) - URI to resource describing the software item
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- Product: "Python", Version: "3.11.5" - Programming language version
- Product: "NI-DAQmx", Version: "23.3.0" - Data acquisition driver
- Product: "TestStand", Version: "2023 Q3" - Test executive software
- Product: "LabVIEW", Version: "2023 Q3" - Measurement software environment
- Product: "Custom Test App", Version: "v2.1.4" - Company-specific test application

Software items help identify if software changes affected test results or reproducibility.

## **Test Description**
A **Test Description** represents a defined test procedure or specification for testing a particular UUT. This defines what tests should be performed.

**Fields:**
- `uut_id` (string) - The ID of the UUT this test is designed for
- `test_description_name` (string) - Name of the test description
- `link` (string) - URI to resource describing the test description
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- "Power Supply Validation Suite" - Complete test suite for power supply products
- "RF Compliance Test Set" - FCC/CE compliance tests for RF devices
- "Functional Verification Protocol" - Basic functionality tests for motor controllers
- "Performance Characterization Tests" - Detailed performance measurements for amplifiers

## **Test**
A **Test** represents an individual test procedure or method. This is more granular than a test description and describes specific test steps.

**Fields:**
- `test_name` (string) - Name of the test
- `description` (string) - Explanation of what the test does
- `link` (string) - URI to resource describing the test
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- "DC Voltage Accuracy Check" - Measures voltage accuracy across specified range
- "Frequency Response Sweep" - Tests frequency response from 20Hz to 20kHz
- "Power-On Self Test" - Automated built-in test executed at startup
- "Load Regulation Test" - Verifies output stability under varying loads

## **Test Adapter**
A **Test Adapter** represents a test fixture, mechanical setup, or interface used to hold, connect, or interface the UUT with the test system.

**Fields:**
- `test_adapter_name` (string) - Name or label for the adapter
- `manufacturer` (string) - Vendor of the adapter
- `model` (string) - Model number or name
- `serial_number` (string) - Unique serial number
- `part_number` (string) - Manufacturer's part number
- `asset_identifier` (string) - For tracking and inventory purposes
- `calibration_due_date` (string) - When calibration expires
- `link` (string) - URI to resource describing the test adapter
- `extensions` (dict) - Custom key-value pairs for additional metadata
- `schema_id` (string) - ID of the schema for extension validation

**Real-world examples**:
- "PCB Test Fixture v2.1" - Custom fixture for holding circuit boards during test
- "RF Connector Adapter Kit" - Set of adapters for different RF connector types
- "Thermal Test Chamber Fixture" - Mechanical setup for environmental testing
- "High Current Test Jig" - Specialized fixture for high-power testing

## **Extension Schema**
An **Extension Schema** defines the structure and validation rules for custom extension fields that can be added to any metadata entity.

**Fields:**
- `schema_id` (string) - Unique identifier for the schema
- `schema` (string) - The schema definition itself (JSON Schema format)

**Real-world examples**:
- Custom fields for tracking calibration certificates
- Additional properties for regulatory compliance data
- Company-specific asset management fields
- Industry-specific metadata requirements

## **Alias**
An **Alias** provides a human-readable name that points to any metadata entity. This creates a layer of abstraction that makes test code more maintainable and readable.

**Fields:**
- `alias_name` (string) - The registered alias name for the metadata instance
- `target_type` (enum) - The type of the aliased metadata instance (see `AliasTargetType` enum)
- `target_id` (string) - The unique identifier for the aliased metadata instance

**Supported Target Types**:
- `UUT_INSTANCE` - Points to a UUT Instance
- `UUT` - Points to a UUT
- `HARDWARE_ITEM` - Points to a Hardware Item  
- `SOFTWARE_ITEM` - Points to a Software Item
- `OPERATOR` - Points to an Operator
- `TEST_DESCRIPTION` - Points to a Test Description
- `TEST` - Points to a Test
- `TEST_STATION` - Points to a Test Station
- `TEST_ADAPTER` - Points to a Test Adapter

**Real-world examples**:
- "Primary_DMM" → points to Hardware Item "NI PXIe-4081 S/N DMM001"
- "Lead_Test_Engineer" → points to Operator "Sarah Johnson"
- "Production_Station_1" → points to Test Station "TestStation_A1"  
- "Current_PowerSupply_Design" → points to UUT "PowerSupply v2.1"

Aliases allow you to change which specific equipment or person is referenced without changing test code.

## **The Metadata Store Hierarchy**
```
Complete Test Execution Context:
├── WHO: Operator "Alex Smith" (Test Engineer)
├── WHERE: Test Station "Station_A1" (Production Line)
├── WHAT: UUT Instance "PS-2024-001" (PowerSupply v2.1)
│   └── Based on UUT "PowerSupply v2.1" (Family: Power)
├── HOW: Test Setup
│   ├── Test Description "Power Supply Validation Suite"
│   ├── Individual Tests
│   │   ├── "DC Voltage Accuracy Check"
│   │   └── "Load Regulation Test"
│   ├── Hardware Items
│   │   ├── "NI PXIe-4081" (Digital Multimeter)
│   │   └── "NI PXIe-5171" (Oscilloscope)
│   └── Test Adapters
│       └── "PCB Test Fixture v2.1"
└── ENVIRONMENT: Software Items
    ├── "Python 3.11.5"
    ├── "NI-DAQmx 23.3.0"
    └── "Custom Test Suite v1.2"

Aliases for Easy Reference:
├── "Primary_Operator" → Alex Smith
├── "Main_Station" → Station_A1  
├── "Test_DMM" → NI PXIe-4081
├── "Current_UUT_Design" → PowerSupply v2.1
└── "Standard_Test_Suite" → Power Supply Validation Suite

Extension Schemas:
├── "Calibration_Certificate_Schema" → Custom calibration tracking
└── "Asset_Management_Schema" → Company inventory fields
```

## **Custom Schemas and Extensions**

Every metadata entity in the NI Metadata Store supports **extensions** - custom key-value pairs that allow you to add organization-specific, industry-specific, or regulatory-specific metadata beyond the standard fields.

### **How Extensions Work**

**Extensions** are a dictionary of custom fields that can be attached to any metadata entity:
```python
# Example: Hardware Item with custom extensions
hardware_item = HardwareItem(
    manufacturer="NI",
    model="PXIe-5171", 
    serial_number="SCOPE001",
    extensions={
        "bandwidth": "1 GHz",
        "manufacture_date": "2024-03-15",
        "calibration_certificate": "CAL-2024-001234",
        "asset_tag": "ASSET-SCOPE-789"
    }
)
```

### **Schema Validation**

To ensure consistency and enforce requirements for extension fields, you can register a **schema** that defines:
- Which extension fields are **required** vs **optional**
- Data types and validation rules
- Field descriptions and constraints

**Schema Registration Process:**
1. **Define the schema** in JSON format (like the example below)
2. **Register the schema** with the metadata store
3. **Get a schema_id** returned from registration
4. **Reference the schema_id** when creating metadata entities

### **Schema Example**

Here's an example schema for oscilloscope hardware items:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/scope.schema.json",
  "title": "Oscilloscope Hardware Item Schema",
  "description": "Schema for oscilloscope hardware item extensions",
  "type": "object",
  "properties": {
    "hardware_item": {
      "type": "object",
      "properties": {
        "bandwidth": {
          "type": "string",
          "description": "Oscilloscope bandwidth specification"
        },
        "manufacture_date": {
          "type": "string",
          "format": "date",
          "description": "Date the hardware was manufactured"
        },
        "calibration_cert": {
          "type": "string",
          "pattern": "^CAL-\\d{4}-\\d{6}$",
          "description": "Calibration certificate number"
        },
        "asset_tag": {
          "type": "string",
          "description": "Company asset tag identifier"
        }
      },
      "required": ["bandwidth", "manufacture_date"]
    }
  }
}
```

**Schema Structure:**
- **Required fields** are listed in the `required` array - must be provided when creating the entity
- **Optional fields** are defined in `properties` but not listed in `required` - can be omitted
- **Descriptions** provide documentation for each field

### **Using Schemas in Practice**

```python
# 1. Register the schema
schema_content = metadata_store_client.register_schema_from_file("scope_schema.json")  # JSON format
schema_id = metadata_store_client.register_schema(schema_content)

# 2. Create hardware item with schema validation
hardware_item = HardwareItem(
    manufacturer="NI",
    model="PXIe-5171",
    serial_number="SCOPE001",
    schema_id=schema_id,  # Links to registered schema
    extensions={
        "bandwidth": "1 GHz",        # Required by schema
        "manufacture_date": "2024-03-15",  # Required by schema
        "asset_tag": "SCOPE-789"     # Optional field
        # Missing calibration_cert is OK (not in required array)
    }
)

# 3. The schema validates extensions during creation
metadata_store_client.create_hardware_item(hardware_item)
```

### **Benefits of Schema Validation**

- **Consistency** - Ensures all entities of the same type have required fields
- **Data Quality** - Prevents missing critical information
- **Documentation** - Schema serves as documentation of expected fields
- **Evolution** - Schemas can be versioned and updated over time
- **Integration** - External systems know what fields to expect

### **Schema Inheritance**

When creating metadata entities within a test result context, schema inheritance applies:
- If the **test result** has a `schema_id`, child entities inherit that schema
- Child entities can override with their own `schema_id` if needed
- This allows consistent validation across entire test sessions

**Example:**
```python
# Test result with schema
test_result = TestResult(
    schema_id="company-standard-v1.2",  # All child entities inherit this
    uut_instance_id=uut_instance_id,
    # ...
)

# Hardware item inherits test result's schema automatically
hardware_item = HardwareItem(
    manufacturer="NI", 
    model="PXIe-4081",
    # schema_id automatically inherited from test_result
    extensions={
        # Fields validated against inherited schema
    }
)
```



## **Benefits of the Digital Thread**
- **Traceability**: Track which operator, equipment, and software were used for any measurement
- **Root Cause Analysis**: Identify patterns related to specific operators, stations, or equipment  
- **Compliance**: Meet regulatory requirements for test documentation and traceability
- **Quality Control**: Monitor operator performance and equipment calibration status
- **Reproducibility**: Recreate test conditions by knowing the complete test context
- **Equipment Management**: Track usage and performance of test equipment over time

This comprehensive metadata foundation enables powerful queries such as:
- "Show me all failed tests from Station A1 last month"
- "Find measurements taken with equipment due for calibration"  
- "Compare results between different operators testing the same UUT model"
- "Identify which test adapter was used for all successful RF tests"
- "Track performance trends for specific UUT instances over time"
- "Find all tests using outdated software versions"
- "Correlate test failures with specific test descriptions or procedures"

## **Extensibility**
All metadata entities support custom extensions through:
- **Extension fields** - Custom key-value pairs for entity-specific data
- **Extension schemas** - Formal validation rules for custom fields
- **Schema inheritance** - Extension schemas can be shared across test results

This allows organizations to add company-specific, industry-specific, or regulatory-specific metadata while maintaining compatibility with the core Metadata Store schemas.