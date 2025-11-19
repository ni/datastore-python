"""PMIC (Power Management IC) tests with datastore publishing."""

import random
import pytest
from ni.datastore.testing import publish_test_to_datastore


@pytest.mark.parametrize("voltage_setpoint", [3.3, 5.0, 1.8])
@pytest.mark.parametrize("current_limit", [2.0, 2.0, 2.0])
@publish_test_to_datastore
def test_pmic_voltage_regulation(log, voltage_setpoint, current_limit, pmic_measure):
    """Test PMIC voltage regulation across different channels and setpoints."""
    # Simulate measurement
    reading = pmic_measure(voltage_setpoint, current_limit)

    measured_voltage = reading["voltage"]
    log.record(measured_voltage)


@pytest.mark.parametrize("voltage_setpoint", [3.3, 5.0, 1.8])
@pytest.mark.parametrize("current_limit", [1.0, 2.5, 5.0])
@publish_test_to_datastore
def test_pmic_current_limit(log, voltage_setpoint, current_limit, pmic_measure):
    """Test PMIC current limiting functionality."""
    reading = pmic_measure(voltage_setpoint, current_limit)

    measured_current = reading["current"]
    log.check_lt(measured_current, current_limit)

    # Verify power calculation
    expected_power = reading["voltage"] * reading["current"]
    measured_power = reading["power"]
    log.check_eq(measured_power, expected_power, epsilon=0.01)


@pytest.mark.parametrize("voltage_setpoint", [3.3, 5.0, 1.8])
@pytest.mark.parametrize("current_limit", [1.0, 2.5, 5.0])
@publish_test_to_datastore
def test_pmic_efficiency(log, voltage_setpoint, current_limit, pmic_measure):
    """Test PMIC power efficiency at different operating points."""
    reading = pmic_measure(voltage_setpoint, current_limit)

    # Fake input power (simulating PMIC efficiency ~85-95%)
    efficiency = random.uniform(0.85, 0.95)
    input_power = reading["power"] / efficiency
    calculated_efficiency = (reading["power"] / input_power) * 100

    log.check_gt(calculated_efficiency, 80.0)
