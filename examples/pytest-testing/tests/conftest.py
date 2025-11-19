"""Pytest configuration and fixtures."""

import random
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file before any fixtures are created
load_dotenv()

# Import fixtures from the datastore testing module
pytest_plugins = ["ni.datastore.testing"]


# PMIC Test Fixtures


@pytest.fixture
def pmic_measure():
    """Simulate a PMIC measurement reading."""

    def measure(voltage_setpoint, current_limit):
        # Fake measurement: add some noise and simulate real behavior
        voltage_reading = voltage_setpoint + random.uniform(-0.05, 0.05)
        current_reading = current_limit * random.uniform(0.3, 0.9)
        return {
            "voltage": voltage_reading,
            "current": current_reading,
            "power": voltage_reading * current_reading,
            "status": ("OK" if abs(voltage_reading - voltage_setpoint) < 0.1 else "FAULT"),
        }

    return measure
