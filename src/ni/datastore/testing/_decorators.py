"""Decorators for pytest tests using the NI Data/Metadata Stores."""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def publish_test_to_datastore(func: F) -> F:
    """Mark your test as participating in measurement data services.

    This decorator verifies that the test function has a DigitalThreadPublisher
    parameter (typically from the 'publisher' fixture) before executing.
    It automatically creates a step for the test and stores the step_id
    on the publisher as 'current_step_id'.

    Example:
        @with_data_publishing
        def test_publish_measurement(publisher):
            # publisher.current_step_id is already set
            publisher.data.publish_measurement(
                name="voltage",
                value=5.0,
                step_id=publisher.current_step_id
            )
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Import here to avoid circular dependency
        from ni.datastore.data import Step
        from ni.datastore.testing._fixtures import DigitalThreadPublisher

        # Find the DigitalThreadPublisher instance
        publisher = None
        for arg in args:
            if isinstance(arg, DigitalThreadPublisher):
                publisher = arg
                break
        if publisher is None:
            for val in kwargs.values():
                if isinstance(val, DigitalThreadPublisher):
                    publisher = val
                    break

        if not publisher:
            raise TypeError(
                f"Test function '{func.__name__}' decorated with @with_data_publishing "
                "must have a DigitalThreadPublisher parameter (e.g., from the 'publisher' fixture)"
            )

        # Check if we've already created a step for this test function
        # This handles parameterized tests - we only create the step once
        if func.__name__ not in publisher._step_ids_by_test:
            # Create a step for this test (first time only)
            step = Step(name=func.__name__, test_result_id=publisher.test_result_id)
            step_id = publisher.data.create_step(step)
            publisher._step_ids_by_test[func.__name__] = step_id

        # Set current_step_id to the step for this test (either newly created or cached)
        publisher.current_step_id = publisher._step_ids_by_test[func.__name__]

        # Publish parameter values as conditions
        # Get the function signature to match parameter names with values
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        # Build a mapping of parameter names to values
        param_values: dict[str, Any] = {}

        # Map positional arguments
        for i, arg in enumerate(args):
            if i < len(param_names):
                param_values[param_names[i]] = arg

        # Add keyword arguments
        param_values.update(kwargs)

        # Publish conditions for supported types (int, str, float, bool)
        for param_name, param_value in param_values.items():
            # Only publish scalar types
            if isinstance(param_value, (int, str, float, bool)):
                publisher.data.publish_condition(
                    name=param_name,
                    condition_type="parameter",
                    value=param_value,
                    step_id=publisher.current_step_id,
                )

        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


__all__ = ["publish_test_to_datastore"]
