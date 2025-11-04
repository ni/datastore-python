# Outcome Enum Wrapper Implementation

This document describes the implementation of a Python wrapper for the gRPC `Outcome` enum type.

## Overview

The `Outcome` enum represents the result of a measurement or test operation. Previously, users had to import and use the protobuf enum directly (`ni.measurements.data.v1.data_store_pb2.Outcome`), which exposed implementation details and used verbose naming conventions.

## Implementation

### Wrapper Class: `Outcome`

Located in `src/ni/datastore/data/_types/_outcome.py`, the wrapper class provides:

1. **Clean API**: Uses shorter, more Pythonic names (`PASSED` vs `OUTCOME_PASSED`)
2. **Type Safety**: Proper Python enum with integer values
3. **Protobuf Integration**: Seamless conversion to/from protobuf types

### Enum Values

```python
class Outcome(IntEnum):
    UNSPECIFIED = 0    # OutcomeProto.OUTCOME_UNSPECIFIED
    PASSED = 1         # OutcomeProto.OUTCOME_PASSED  
    FAILED = 2         # OutcomeProto.OUTCOME_FAILED
    INDETERMINATE = 3  # OutcomeProto.OUTCOME_INDETERMINATE
```

### Conversion Methods

- `from_protobuf(outcome_proto)`: Creates wrapper from protobuf enum value
- `to_protobuf()`: Converts wrapper to protobuf enum value

## Usage

### Before (Direct Protobuf Usage)
```python
from ni.measurements.data.v1.data_store_pb2 import Outcome

data_store_client.publish_measurement(
    measurement_name="temperature",
    value=23.5,
    step_id="step-123",
    outcome=Outcome.OUTCOME_PASSED
)
```

### After (Wrapper Usage)
```python
from ni.datastore.data import Outcome

data_store_client.publish_measurement(
    measurement_name="temperature", 
    value=23.5,
    step_id="step-123",
    outcome=Outcome.PASSED
)
```

## Benefits

1. **Cleaner API**: More readable enum names
2. **Better Integration**: Exported from main package
3. **Type Safety**: Proper Python enum with validation
4. **Backward Compatibility**: Internal protobuf usage unchanged
5. **Future-Proof**: Easier to extend or modify without breaking changes

## Files Modified

- `src/ni/datastore/data/_types/_outcome.py` - New wrapper class
- `src/ni/datastore/data/__init__.py` - Export wrapper instead of protobuf type
- `src/ni/datastore/data/_data_store_client.py` - Use wrapper in API, convert to protobuf internally
- `tests/unit/data/test_publish_measurement.py` - Updated tests to use wrapper
- `tests/unit/data/test_outcome.py` - New comprehensive tests for wrapper

## Design Notes

For enum wrappers, we use `IntEnum` which:
- Inherits from both `int` and `Enum`
- Provides integer comparison capabilities
- Maintains enum semantics and iteration
- Allows easy conversion to/from protobuf integer values

The wrapper handles the conversion automatically in the DataStoreClient methods, so users only work with the clean enum interface while the gRPC layer still receives the expected protobuf types.