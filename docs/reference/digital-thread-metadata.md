# NI Digital Thread Metadata

The NI Digital Thread captures the metadata that describes **who**, **what**, **where**, and **how** tests are performed. This creates a complete context around your test data, enabling traceability and analysis across your entire test ecosystem.

## **Operator**
An **Operator** represents a person who performs tests or operates test equipment. This captures the human element in your test process.

**Real-world examples**:
- "Sarah Johnson" - Test Engineer who runs daily production tests
- "Mike Chen" - Senior Technician who performs calibrations  
- "Alex Smith" - Lab Assistant who conducts R&D validation tests

Each operator has a role (e.g., "Test Engineer", "Lab Technician", "Quality Inspector") that helps categorize their responsibilities and skill level.

## **Test Station**
A **Test Station** represents a physical location or setup where testing is performed. This could be a bench, rack, or dedicated test system.

**Real-world examples**:
- "Station_A1" - Production line station #1 for power supply testing
- "Bench_RF_Lab" - RF laboratory bench with spectrum analyzers
- "Burn_In_Rack_3" - Environmental stress testing chamber
- "Cal_Lab_Station" - Precision calibration workstation with reference standards

Test stations help track where tests were performed, enabling analysis of station-specific issues or performance variations.

## **Hardware Item**
A **Hardware Item** represents test equipment, instruments, or tools used during testing. This captures what physical equipment was involved in generating the measurements.

**Real-world examples**:
- Manufacturer: "NI", Model: "PXIe-4081", Serial: "DMM001" - Digital multimeter
- Manufacturer: "Keysight", Model: "E5071C", Serial: "VNA789" - Vector network analyzer  
- Manufacturer: "Tektronix", Model: "MSO64", Serial: "SCOPE456" - Mixed-signal oscilloscope
- Manufacturer: "Fluke", Model: "8588A", Serial: "REF123" - Reference multimeter

Hardware items include calibration information and help ensure measurement traceability.

## **UUT (Unit Under Test)**
A **UUT** represents a product definition or model being tested. This is the "what" - the type of device or product under test.

**Real-world examples**:
- Model: "PowerSupply v2.1", Family: "Power" - A specific power supply product
- Model: "Audio Amplifier v1.3", Family: "Audio" - An audio amplifier design
- Model: "RF Transceiver Gen3", Family: "Communications" - A radio frequency module
- Model: "Motor Controller v4.0", Family: "Industrial" - An industrial motor controller

UUTs represent the product designs, while UUT instances represent individual physical devices.

## **UUT Instance**
A **UUT Instance** represents an individual physical device with a unique serial number. This is a specific unit of the UUT model being tested.

**Real-world examples**:
- UUT: "PowerSupply v2.1", Serial: "PS-2024-001" - First power supply unit built in 2024
- UUT: "Audio Amplifier v1.3", Serial: "AMP-2024-456" - Specific amplifier with serial number
- UUT: "RF Transceiver Gen3", Serial: "RF-X7G9-2024-789" - Individual transceiver unit

Each UUT instance tracks the test history for that specific physical device throughout its lifecycle.

## **Software Item**
A **Software Item** represents software tools, environments, or versions used during testing. This captures the software context that could affect test results.

**Real-world examples**:
- Product: "Python", Version: "3.11.5" - Programming language version
- Product: "NI-DAQmx", Version: "23.3.0" - Data acquisition driver
- Product: "TestStand", Version: "2023 Q3" - Test executive software
- Product: "LabVIEW", Version: "2023 Q3" - Measurement software environment
- Product: "Custom Test App", Version: "v2.1.4" - Company-specific test application

Software items help identify if software changes affected test results or reproducibility.

## **Alias**
An **Alias** provides a human-readable name that points to any metadata entity. This creates a layer of abstraction that makes test code more maintainable and readable.

**Real-world examples**:
- "Primary_DMM" → points to Hardware Item "NI PXIe-4081 S/N DMM001"
- "Lead_Test_Engineer" → points to Operator "Sarah Johnson"
- "Production_Station_1" → points to Test Station "TestStation_A1"  
- "Current_PowerSupply_Design" → points to UUT "PowerSupply v2.1"

Aliases allow you to change which specific equipment or person is referenced without changing test code.

## **The Digital Thread Hierarchy**
```
Test Execution Context:
├── WHO: Operator "Alex Smith" (Test Engineer)
├── WHERE: Test Station "Station_A1" (Production Line)
├── WHAT: UUT Instance "PS-2024-001" (PowerSupply v2.1)
├── HOW: Hardware Items
│   ├── "NI PXIe-4081" (Digital Multimeter)
│   └── "NI PXIe-5171" (Oscilloscope) 
└── ENVIRONMENT: Software Items
    ├── "Python 3.11.5"
    ├── "NI-DAQmx 23.3.0"
    └── "Custom Test Suite v1.2"

Aliases for Easy Reference:
├── "Primary_Operator" → Alex Smith
├── "Main_Station" → Station_A1
├── "Test_DMM" → NI PXIe-4081
└── "Current_UUT_Design" → PowerSupply v2.1
```

## **Benefits of the Digital Thread**
- **Traceability**: Track which operator, equipment, and software were used for any measurement
- **Root Cause Analysis**: Identify patterns related to specific operators, stations, or equipment  
- **Compliance**: Meet regulatory requirements for test documentation and traceability
- **Quality Control**: Monitor operator performance and equipment calibration status
- **Reproducibility**: Recreate test conditions by knowing the complete test context
- **Equipment Management**: Track usage and performance of test equipment over time

This metadata foundation enables powerful queries like "Show me all failed tests from Station A1 last month" or "Find measurements taken with equipment due for calibration" or "Compare results between different operators testing the same UUT model".