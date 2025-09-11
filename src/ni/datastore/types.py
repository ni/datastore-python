from enum import Enum

class Measurement:
    """Minimal Measurement class."""

    def __init__(self):
        pass

class StoredDataValue:
    """Minimal StoredDataValue class."""

    def __init__(self):
        pass

class PassFailStatus(Enum):
    PASS_FAIL_STATUS_UNSPECIFIED = 0
    PASS_FAIL_STATUS_PASSED = 1
    PASS_FAIL_STATUS_FAILED = 2
    PASS_FAIL_STATUS_INDETERMINATE = 3

class Moniker:
    """Minimal Moniker class."""

    def __init__(self):
        pass