# NI Measurement Data Store

The NI Measurement Data Store includes these objects:

## **TestResult**
A **TestResult** represents a complete test session or test execution run for a specific Unit Under Test (UUT). It's the top-level container that captures everything that happened when you tested a particular device.

**Real-world example**: When you put a circuit board on a test station and run a complete validation sequence, that entire session becomes one TestResult. It includes metadata like who ran the test, when it was run, what test station was used, and links to all the measurements and steps that were performed.

## **Step**
A **Step** represents an individual test procedure or operation within a larger test sequence. Each step typically tests a specific aspect or function of the UUT.

**Real-world examples**:
- "Measure DC Voltage on Pin 5" 
- "Verify Communication Protocol Response"
- "Check LED Brightness at 100mA"
- "Functional Test - Power On Sequence"
- "Calibration - Set Reference Voltage"

Each step belongs to a TestResult and can contain multiple measurements and conditions.

## **Measurement**
A **Measurement** is the actual data captured during a test step - the raw values, waveforms, or results from instruments or test equipment.

**Real-world examples**:
- A voltage reading: `3.297V` from a multimeter
- A waveform: Time-series data from an oscilloscope showing a signal over time
- A frequency measurement: `1.0234 MHz` from a frequency counter  
- A boolean result: `PASS/FAIL` from a functional test
- An array of values: Temperature readings over time from a thermal sensor

## **The Hierarchy**
```
TestResult (Test session for Serial# ABC123)
├── Step 1: "Power Supply Verification"
│   ├── Measurement: "5V Rail Voltage" = 5.02V
│   ├── Measurement: "Current Draw" = 245mA
│   └── Condition: "Temperature" = 23.5°C
├── Step 2: "Digital I/O Test"
│   ├── Measurement: "Pin 1 High Level" = 3.28V
│   └── Measurement: "Pin 2 Response Time" = 150μs
└── Step 3: "Communication Test"
    └── Measurement: "UART Data Rate" = 115200 bps
```

This structure allows you to drill down from "what test was run" (TestResult) to "what specific tests were performed" (Steps) to "what were the actual measured values" (Measurements).