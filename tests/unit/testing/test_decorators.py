"""Tests for ni.datastore.testing._decorators module.

This module tests the decorators provided by the testing package.
"""

from ni.datastore.testing import publish_test_to_datastore


def test_with_measurement_data_service_decorator():
    """Test that the decorator can be applied to a function."""

    @publish_test_to_datastore
    def sample_test():
        return "test_result"

    result = sample_test()
    assert result == "test_result"


def test_with_measurement_data_service_preserves_function_name():
    """Test that the decorator preserves the original function's name."""

    @publish_test_to_datastore
    def my_test_function():
        pass

    assert my_test_function.__name__ == "my_test_function"


def test_with_measurement_data_service_preserves_docstring():
    """Test that the decorator preserves the original function's docstring."""

    @publish_test_to_datastore
    def my_test_function():
        """This is my test docstring."""
        pass

    assert my_test_function.__doc__ == "This is my test docstring."
