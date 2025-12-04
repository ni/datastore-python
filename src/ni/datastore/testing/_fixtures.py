"""Pytest fixtures for tests using the NI Data/Metadata Stores."""

from __future__ import annotations

import getpass
import inspect
import os
import socket
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import grpc
import pytest
import pytest_check as check
from ni.datastore.data import DataStoreClient, Outcome, TestResult
from ni.datastore.metadata import MetadataStoreClient, Operator, TestStation

if TYPE_CHECKING:
    from collections.abc import Generator

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


def _is_literal_or_expression(arg_text: str) -> tuple[bool, str]:
    """Check if the argument text is a literal value or expression.

    Args:
        arg_text: The extracted argument text from source code.

    Returns:
        A tuple of (is_literal_or_expression, description) where:
        - is_literal_or_expression: True if it's a literal or expression
        - description: A description of what was detected (e.g., "literal", "expression")
    """
    # Check if it's a literal (starts with digit, quote, True, False, None)
    if (
        arg_text[0].isdigit()
        or arg_text[0] in ('"', "'")
        or arg_text in ("True", "False", "None")
        or arg_text.startswith("0x")
        or arg_text.startswith("0b")
        or arg_text.startswith("0o")
    ):
        return (True, "literal")

    # Check for expressions (contains operators)
    if any(
        op in arg_text
        for op in [
            "+",
            "-",
            "*",
            "/",
            "//",
            "%",
            "**",
            "&",
            "|",
            "^",
            "<<",
            ">>",
            "(",
            "[",
        ]
    ):
        return (True, "expression")

    return (False, "")


def _extract_variable_name(method_name: str, frame_depth: int = 1) -> str:
    """Extract the variable name from the calling code.

    Uses frame introspection to examine the source code of the caller and
    extract the first argument passed to the specified method.

    Args:
        method_name: The name of the method being called (e.g., "record").
        frame_depth: How many frames up to look (1 = immediate caller,
            2 = caller's caller, etc.). Default is 1.

    Returns:
        str: The extracted variable name.

    Raises:
        RuntimeError: If unable to access frames or parse the call.
        ValueError: If a literal or expression is detected instead of a variable.
    """
    import re

    # Get the calling frame
    frame = inspect.currentframe()
    if frame is None:
        raise RuntimeError("Unable to access calling frame")

    target_frame = None
    try:
        # Navigate to the target frame
        target_frame = frame
        for _ in range(frame_depth):
            if target_frame.f_back is None:
                raise RuntimeError(f"Unable to access frame at depth {frame_depth}")
            target_frame = target_frame.f_back

        # Get the code context (the line that called the method)
        caller_info = inspect.getframeinfo(target_frame, context=1)
        if caller_info.code_context is None:
            raise RuntimeError("Unable to access source code context")

        call_line = caller_info.code_context[0].strip()

        # Extract the argument from the method call
        # Look for pattern: .method_name(variable_name) or .method_name(variable_name, ...)
        pattern = rf"\.{method_name}\s*\(\s*([^),]+)"
        match = re.search(pattern, call_line)
        if not match:
            raise RuntimeError(f"Unable to parse {method_name}() call from: {call_line}")

        arg_text = match.group(1).strip()

        # Check if it's a literal or expression
        is_invalid, invalid_type = _is_literal_or_expression(arg_text)
        if is_invalid:
            raise ValueError(
                f"{method_name}() requires a variable reference or explicit name parameter "
                f"when passing a {invalid_type} value. Got: {arg_text}"
            )

        return arg_text

    finally:
        # Clean up frame references to avoid reference cycles
        del frame
        if target_frame is not None:
            del target_frame


class DigitalThreadPublisher:
    """Publisher for both data and metadata to the NI Data/Metadata Stores.

    This class provides access to both DataStoreClient and MetadataStoreClient,
    allowing tests to publish measurements, conditions, and metadata.

    Attributes:
        data: The DataStoreClient for publishing measurements and conditions.
        metadata: The MetadataStoreClient for publishing metadata.
        test_result_id: The ID of the test result created for this test session.
        current_step_id: The ID of the current step being executed.
    """

    def __init__(
        self,
        data_client: DataStoreClient,
        metadata_client: MetadataStoreClient,
        channel: grpc.Channel | None = None,
    ) -> None:
        """Initialize the DigitalThreadPublisher.

        Args:
            data_client: The DataStoreClient instance.
            metadata_client: The MetadataStoreClient instance.
            channel: Optional gRPC channel that was created for the clients.
        """
        self.data = data_client
        self.metadata = metadata_client
        self._channel = channel
        self.test_result_id: str = ""
        self.current_step_id: str = ""
        self._step_ids_by_test: dict[str, str] = {}

    def __enter__(self) -> Self:
        """Enter the runtime context of the publisher."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit the runtime context of the publisher."""
        self.close()

    def close(self) -> None:
        """Close both clients and the gRPC channel if it was created."""
        self.data.close()
        self.metadata.close()
        if self._channel is not None:
            self._channel.close()

    def record(self, value: bool | int | float | str, name: str | None = None) -> str:
        """Record a scalar measurement using the variable name as the measurement name.

        This is a convenience method that inspects the calling code to extract
        the variable name and publishes it as a measurement. Alternatively, you
        can explicitly provide the measurement name.

        Args:
            value: The scalar value to publish (bool, int, float, or str).
                Must be passed as a variable reference if name is not provided.
            name: Optional explicit name for the measurement. If not provided,
                the variable name will be extracted from the calling code.

        Returns:
            str: The ID of the published measurement.

        Raises:
            TypeError: If the value is not a scalar type (bool, int, float, str).
            ValueError: If name is not provided and a literal value is passed
                instead of a variable reference.
            RuntimeError: If name is not provided and the variable name cannot
                be determined from the source.

        Example:
            voltage = 5.0
            # Using automatic variable name extraction
            log.record(voltage)  # Publishes measurement named "voltage" with value 5.0

            # Using explicit name
            log.record(5.0, name="voltage")  # Publishes measurement named "voltage" with value 5.0

            # This will raise ValueError (literal not allowed without name):
            # log.record(5.0)
        """
        # Validate type
        if not isinstance(value, (bool, int, float, str)):
            raise TypeError(
                f"record() only supports scalar types (bool, int, float, str), "
                f"got {type(value).__name__}"
            )

        # If name is provided, use it directly
        if name is not None:
            variable_name = name
        else:
            # Extract variable name from calling code
            variable_name = _extract_variable_name("record", frame_depth=2)

        # Publish the measurement
        measurement_id = self.data.publish_measurement(
            name=variable_name,
            value=value,
            step_id=self.current_step_id,
        )

        return measurement_id

    def check_gt(
        self,
        value: float,
        expected: float,
        name: str | None = None,
    ) -> str:
        """Assert that value is greater than expected and publish the measurement with outcome.

        Uses pytest's assertion mechanism to fail the test if the condition is not met.
        The measurement is published with PASSED outcome if the assertion succeeds,
        or FAILED outcome if it fails.

        Args:
            value: The float value to compare and publish.
                Must be passed as a variable reference if name is not provided.
            expected: The value to compare against.
            name: Optional explicit name for the measurement. If not provided,
                the variable name will be extracted from the calling code.

        Returns:
            str: The ID of the published measurement.

        Raises:
            AssertionError: If value is not greater than expected.
            TypeError: If the value is not a float.
            ValueError: If name is not provided and a literal value is passed
                instead of a variable reference.
            RuntimeError: If name is not provided and the variable name cannot
                be determined from the source.

        Example:
            voltage = 5.0
            log.assert_gt(voltage, 3.0)  # Passes and publishes with PASSED outcome
            log.assert_gt(voltage, 10.0)  # Fails assertion and publishes with FAILED outcome
        """
        # Validate type
        if not isinstance(value, float):
            raise TypeError(f"assert_gt() only supports float type, got {type(value).__name__}")

        # If name is provided, use it directly
        if name is not None:
            variable_name = name
        else:
            # Extract variable name from calling code
            variable_name = _extract_variable_name("check_gt", frame_depth=2)

        # Perform the assertion and determine outcome
        passed = check.greater(
            value,
            expected,
            msg=f"{variable_name} ({value}) is not greater than {expected}",
        )
        outcome = Outcome.PASSED if passed else Outcome.FAILED

        # Publish the measurement with outcome
        measurement_id = self.data.publish_measurement(
            name=variable_name,
            value=value,
            step_id=self.current_step_id,
            outcome=outcome,
        )

        return measurement_id

    def check_lt(
        self,
        value: float,
        expected: float,
        name: str | None = None,
    ) -> str:
        """Check that value is less than expected and publish the measurement with outcome.

        Uses pytest_check to record the check result without immediately failing the test.
        The measurement is published with PASSED outcome if the check succeeds,
        or FAILED outcome if it fails.

        Args:
            value: The float value to compare and publish.
                Must be passed as a variable reference if name is not provided.
            expected: The value to compare against.
            name: Optional explicit name for the measurement. If not provided,
                the variable name will be extracted from the calling code.

        Returns:
            str: The ID of the published measurement.

        Raises:
            TypeError: If the value is not a float.
            ValueError: If name is not provided and a literal value is passed
                instead of a variable reference.
            RuntimeError: If name is not provided and the variable name cannot
                be determined from the source.

        Example:
            voltage = 3.0
            log.check_lt(voltage, 5.0)  # Passes and publishes with PASSED outcome
            log.check_lt(voltage, 2.0)  # Fails check and publishes with FAILED outcome
        """
        # Validate type
        if not isinstance(value, float):
            raise TypeError(f"check_lt() only supports float type, got {type(value).__name__}")

        # If name is provided, use it directly
        if name is not None:
            variable_name = name
        else:
            # Extract variable name from calling code
            variable_name = _extract_variable_name("check_lt", frame_depth=2)

        # Perform the check and determine outcome
        passed = check.less(
            value,
            expected,
            msg=f"{variable_name} ({value}) is not less than {expected}",
        )
        outcome = Outcome.PASSED if passed else Outcome.FAILED

        # Publish the measurement with outcome
        measurement_id = self.data.publish_measurement(
            name=variable_name,
            value=value,
            step_id=self.current_step_id,
            outcome=outcome,
        )

        return measurement_id

    def check_eq(
        self,
        value: float,
        expected: float,
        epsilon: float = 0.1,
        name: str | None = None,
    ) -> str:
        """Check that value equals expected within epsilon tolerance and publish the measurement with outcome.

        Uses pytest_check to record the check result without immediately failing the test.
        The measurement is published with PASSED outcome if the check succeeds,
        or FAILED outcome if it fails.

        Args:
            value: The float value to compare and publish.
                Must be passed as a variable reference if name is not provided.
            expected: The value to compare against.
            epsilon: The allowed deviation (tolerance) for the comparison.
                The check passes if abs(value - expected) <= epsilon.
            name: Optional explicit name for the measurement. If not provided,
                the variable name will be extracted from the calling code.

        Returns:
            str: The ID of the published measurement.

        Raises:
            TypeError: If the value is not a float.
            ValueError: If name is not provided and a literal value is passed
                instead of a variable reference, or if epsilon is negative.
            RuntimeError: If name is not provided and the variable name cannot
                be determined from the source.

        Example:
            voltage = 5.0
            log.check_eq(voltage, 5.0, 0.1)  # Passes (exact match)
            log.check_eq(voltage, 5.05, 0.1)  # Passes (within tolerance)
            log.check_eq(voltage, 3.0, 0.1)  # Fails check
        """
        # Validate types
        if not isinstance(value, float):
            raise TypeError(f"check_eq() only supports float type, got {type(value).__name__}")
        if epsilon < 0:
            raise ValueError(f"epsilon must be non-negative, got {epsilon}")

        # If name is provided, use it directly
        if name is not None:
            variable_name = name
        else:
            # Extract variable name from calling code
            variable_name = _extract_variable_name("check_eq", frame_depth=2)

        # Perform the check and determine outcome
        diff = abs(value - expected)
        passed = check.less_equal(
            diff,
            epsilon,
            msg=f"{variable_name} ({value}) differs from {expected} by {diff}, exceeds epsilon {epsilon}",
        )
        outcome = Outcome.PASSED if passed else Outcome.FAILED

        # Publish the measurement with outcome
        measurement_id = self.data.publish_measurement(
            name=variable_name,
            value=value,
            step_id=self.current_step_id,
            outcome=outcome,
        )

        return measurement_id


@pytest.fixture(scope="module")
def log(
    request: pytest.FixtureRequest,
) -> Generator[DigitalThreadPublisher, None, None]:
    """Pytest fixture that provides a DigitalThreadPublisher for testing.

    This fixture automatically sets up the test environment by:
    1. Creating data and metadata store clients
    2. Registering schemas if found (module.schema.json/toml or test.schema.json/toml)
    3. Creating metadata from registration files if found (module.registration.json or test.registration.json)
    4. Creating default operator and test station if not provided
    5. Creating a test result for the test module

    The publisher is yielded for use in tests and properly cleaned up on teardown.

    Environment Variables:
        DATASTORE_HOST: The hostname or IP address of the service
        DATASTORE_PORT: The port number of the service
        DATASTORE_JWT_TOKEN: Optional JWT token override for testing
        DATASTORE_USE_INSECURE_CHANNEL: Set to 'true' to force insecure channels
            for all targets (useful for private network deployments)
        DATASTORE_DISABLE_AUTH: Set to 'true' to disable authentication entirely
            and use basic GrpcChannelPool instead of AuthGrpcChannelPool.
            Note: Should only be used with DATASTORE_USE_INSECURE_CHANNEL=true
            for local/testing scenarios (secure channels require authentication)

    Note:
        JWT tokens are automatically obtained from the nigel CLI executable.
        For testing purposes, DATASTORE_JWT_TOKEN can be set to bypass
        the auth daemon and use a specific token.

    Example:
        def test_publish_measurement(publisher):
            # Publisher already has test_result_id set
            step_id = publisher.data.create_step(...)
    """
    host = os.environ.get("DATASTORE_HOST")
    port = os.environ.get("DATASTORE_PORT")

    channel = None

    # Check if authentication is disabled
    disable_auth = os.environ.get("DATASTORE_DISABLE_AUTH", "").lower() in (
        "true",
        "1",
        "yes",
    )

    # If both host and port are set, create a channel pool with optional auth support
    # JWT token will be obtained automatically from the auth daemon if auth is enabled
    if host and port:
        if disable_auth:
            # Use basic GrpcChannelPool without authentication
            from ni_grpc_extensions.channelpool import GrpcChannelPool

            pool = GrpcChannelPool()
        else:
            # Use authenticated channel pool
            from ni.datastore._auth import AuthGrpcChannelPool

            pool = AuthGrpcChannelPool()

        channel = pool.get_channel(f"{host}:{port}")

        data_client = DataStoreClient(grpc_channel=channel, grpc_channel_pool=pool)
        metadata_client = MetadataStoreClient(grpc_channel=channel, grpc_channel_pool=pool)
    else:
        # No parameters - use default discovery for both clients
        data_client = DataStoreClient()
        metadata_client = MetadataStoreClient()

    publisher_instance = DigitalThreadPublisher(data_client, metadata_client, channel)

    # Get information about the test module
    current_user = getpass.getuser()
    computer_name = socket.gethostname()

    # Get the module that is using the fixture
    # Use request.path (pytest 7+) or request.fspath for the actual test file path
    if hasattr(request, "path"):
        module_path = Path(request.path)
    elif hasattr(request, "fspath"):
        module_path = Path(str(request.fspath))  # type: ignore[attr-defined]
    else:
        # Fallback for older pytest versions
        test_module = inspect.getmodule(request.node)
        if test_module is None or test_module.__file__ is None:
            module_path = Path.cwd() / "unknown_test.py"
        else:
            module_path = Path(test_module.__file__)

    module_dir = module_path.parent
    module_name = module_path.stem

    # Check for schema files (test files take precedence over module files)
    schema_file = None
    for name_prefix in [module_name, "module"]:
        for ext in ["json", "toml"]:
            candidate = module_dir / f"{name_prefix}.schema.{ext}"
            if candidate.exists():
                schema_file = candidate
                break
        if schema_file:
            break

    # Check for registration files (test files take precedence over module files)
    registration_file = None
    for name_prefix in [module_name, "module"]:
        candidate = module_dir / f"{name_prefix}.registration.json"
        if candidate.exists():
            registration_file = candidate
            break

    # Register schema if found
    schema_id = ""
    if schema_file:
        schema_id = publisher_instance.metadata.register_schema_from_file(schema_file)

    # Create metadata from registration file if found
    metadata_items = None
    if registration_file:
        metadata_items = publisher_instance.metadata.create_from_json_file(registration_file)

    # Determine operator_id
    operator_id = ""
    if metadata_items and metadata_items.operators:
        if len(metadata_items.operators) > 1:
            raise ValueError(
                "Registration file contains multiple operators. "
                "Test result can only have one operator."
            )
        operator_id = metadata_items.operators[0].id
    else:
        # Create default operator with current user
        operator = Operator(name=current_user, schema_id=schema_id if schema_id else "")
        operator_id = publisher_instance.metadata.create_operator(operator)

    # Determine test_station_id
    test_station_id = ""
    if metadata_items and metadata_items.test_stations:
        if len(metadata_items.test_stations) > 1:
            raise ValueError(
                "Registration file contains multiple test stations. "
                "Test result can only have one test station."
            )
        test_station_id = metadata_items.test_stations[0].id
    else:
        # Create default test station with computer name
        test_station = TestStation(name=computer_name, schema_id=schema_id if schema_id else "")
        test_station_id = publisher_instance.metadata.create_test_station(test_station)

    # Create test result
    test_result = TestResult(
        name=module_name,
        operator_id=operator_id,
        test_station_id=test_station_id,
        schema_id=schema_id if schema_id else "",
    )

    # Add additional metadata from registration file if available
    if metadata_items:
        if metadata_items.uut_instances:
            if len(metadata_items.uut_instances) > 1:
                raise ValueError(
                    "Registration file contains multiple UUT instances. "
                    "Test result can only have one UUT instance."
                )
            test_result.uut_instance_id = metadata_items.uut_instances[0].id

        if metadata_items.test_descriptions:
            if len(metadata_items.test_descriptions) > 1:
                raise ValueError(
                    "Registration file contains multiple test descriptions. "
                    "Test result can only have one test description."
                )
            test_result.test_description_id = metadata_items.test_descriptions[0].id

        # Add all hardware items, software items, and test adapters
        if metadata_items.hardware_items:
            test_result.hardware_item_ids.extend(
                [item.id for item in metadata_items.hardware_items]
            )
        if metadata_items.software_items:
            test_result.software_item_ids.extend(
                [item.id for item in metadata_items.software_items]
            )
        if metadata_items.test_adapters:
            test_result.test_adapter_ids.extend(
                [adapter.id for adapter in metadata_items.test_adapters]
            )

    # Create the test result and store its ID
    publisher_instance.test_result_id = publisher_instance.data.create_test_result(test_result)

    yield publisher_instance

    # Cleanup
    publisher_instance.close()


__all__ = ["DigitalThreadPublisher", "log"]
