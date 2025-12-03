import base64
import collections
import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import grpc
from ni_grpc_extensions.channelpool import GrpcChannelPool

_logger = logging.getLogger(__name__)


class _ClientCallDetails(
    collections.namedtuple(
        "_ClientCallDetails",
        (
            "method",
            "timeout",
            "metadata",
            "credentials",
            "wait_for_ready",
            "compression",
        ),
    ),
    grpc.ClientCallDetails,
):
    pass


# Create an interceptor that adds the Authorization header
class _AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, token_provider: "JwtTokenProvider"):
        self._token_provider = token_provider

    def _add_auth_metadata(self, client_call_details):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)

        token = self._token_provider.get_token()
        metadata.append(("authorization", f"Bearer {token}"))

        return _ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            metadata,
            client_call_details.credentials,
            client_call_details.wait_for_ready,
            client_call_details.compression,
        )

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details = self._add_auth_metadata(client_call_details)
        return continuation(new_details, request)


class JwtTokenProvider:
    """Provides JWT tokens from the nigel authentication daemon."""

    def __init__(self, grpc_channel_pool: Optional[GrpcChannelPool] = None) -> None:
        """Initialize the JWT token provider.

        Args:
            grpc_channel_pool: Optional gRPC channel pool for making requests.
                If not provided, a new one will be created.
        """
        self._grpc_channel_pool = grpc_channel_pool or GrpcChannelPool()
        self._cached_token: Optional[str] = None

    def get_token(self) -> str:
        """Get a JWT token from the nigel authentication daemon.

        First attempts to use the DATASTORE_JWT_TOKEN environment variable.
        Then tries to get the token via the nigel CLI executable.
        In the future, we should use gRPC to communicate with the auth daemon directly.

        Returns:
            The JWT token string.

        Raises:
            RuntimeError: If unable to obtain the JWT token.
        """
        # Check for environment variable override first (for testing)
        env_token = os.environ.get("DATASTORE_JWT_TOKEN")
        if env_token:
            _logger.debug("Using JWT token from DATASTORE_JWT_TOKEN environment variable")
            return env_token

        # Check if we have a cached token that hasn't expired
        if self._cached_token and not self._is_token_expired(self._cached_token):
            _logger.debug("Using cached JWT token")
            return self._cached_token

        if self._cached_token:
            _logger.debug("Cached token expired, fetching new token")

        # Try CLI-based approach first (temporary implementation)
        nigel_path = self._find_nigel_executable()
        if nigel_path:
            try:
                _logger.debug(f"Getting JWT token from nigel CLI at: {nigel_path}")
                self._cached_token = self._get_token_from_cli(nigel_path)
                return self._cached_token
            except Exception as e:
                _logger.warning(f"Failed to get token from nigel CLI: {e}")
                # Fall through to try gRPC approach

        raise RuntimeError(
            "Unable to obtain JWT token. Tried:\n"
            "1. DATASTORE_JWT_TOKEN environment variable (not set)\n"
            f"2. nigel CLI executable (not at '{os.environ.get('NIGEL_CLI_PATH')}' or in the PATH)\n"
            "To resolve, do one of the following:\n"
            "- Set DATASTORE_JWT_TOKEN environment variable with a valid tokenr\n"
            "- Install the nigel CLI and ensure it's in your PATH or set NIGEL_CLI_PATH"
        )

    @staticmethod
    def _find_nigel_executable() -> Optional[str]:
        """Find the nigel CLI executable on the system.

        Searches for the nigel executable in the following order:
        1. NIGEL_CLI_PATH environment variable (if set)
        2. System PATH

        Returns:
            The full path to the nigel executable, or None if not found.
        """
        # Check environment variable first
        env_path = os.environ.get("NIGEL_CLI_PATH")
        if env_path:
            nigel_path = Path(env_path)
            if nigel_path.exists() and nigel_path.is_file():
                _logger.debug(f"Found nigel at NIGEL_CLI_PATH: {nigel_path}")
                return str(nigel_path)

        # Check if nigel is in the system PATH
        nigel_in_path = shutil.which("nigel")
        if nigel_in_path:
            _logger.debug(f"Found nigel in PATH: {nigel_in_path}")
            return nigel_in_path

        _logger.warning("Could not find nigel executable")
        return None

    @staticmethod
    def _get_token_from_cli(nigel_path: str) -> str:
        """Get JWT token by calling the nigel CLI.

        Args:
            nigel_path: Path to the nigel executable.

        Returns:
            The JWT token string.

        Raises:
            RuntimeError: If the CLI call fails or returns invalid output.
        """
        try:
            result = subprocess.run(
                [nigel_path, "auth", "token"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )

            token = result.stdout.strip()
            if not token:
                raise RuntimeError("nigel CLI returned empty output")

            return token

        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"nigel CLI timed out after 10 seconds") from e
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else "No error output"
            raise RuntimeError(f"nigel CLI failed with exit code {e.returncode}: {stderr}") from e
        except FileNotFoundError as e:
            raise RuntimeError(f"nigel executable not found at: {nigel_path}") from e

    @staticmethod
    def _is_token_expired(token: str, buffer_seconds: int = 60) -> bool:
        """Check if a JWT token is expired or about to expire.

        Args:
            token: The JWT token string.
            buffer_seconds: Number of seconds before actual expiration to consider
                the token expired (default: 60). This provides a safety margin.

        Returns:
            True if the token is expired or will expire within buffer_seconds,
            False otherwise.
        """
        try:
            # JWT format: header.payload.signature
            # We only need the payload (middle section)
            parts = token.split(".")
            if len(parts) != 3:
                _logger.warning("Invalid JWT token format (expected 3 parts)")
                return True  # Treat invalid tokens as expired

            # Decode the payload (base64url encoded)
            # Add padding if necessary (base64 requires length to be multiple of 4)
            payload_b64 = parts[1]
            padding = 4 - (len(payload_b64) % 4)
            if padding != 4:
                payload_b64 += "=" * padding

            # Decode from base64url to JSON
            payload_json = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
            payload = json.loads(payload_json)

            # Check expiration claim
            exp = payload.get("exp")
            if exp is None:
                _logger.warning("JWT token missing 'exp' claim")
                return True  # Treat tokens without expiration as expired for safety

            # Compare with current time (with buffer)
            current_time = time.time()
            expires_at = exp - buffer_seconds

            if current_time >= expires_at:
                _logger.debug(
                    f"Token expired or expiring soon (exp: {exp}, current: {current_time})"
                )
                return True

            return False

        except Exception as e:
            _logger.warning(f"Error checking token expiration: {e}")
            return True  # Treat any errors as expired for safety


class AuthGrpcChannelPool(GrpcChannelPool):
    def __init__(self, jwt_token: Optional[str] = None) -> None:
        """Initialize the authenticated gRPC channel pool.

        By default, secure channels (with SSL/TLS) are used for non-local targets.
        This can be overridden using the DATASTORE_USE_INSECURE_CHANNEL environment
        variable for private network deployments where TLS is not required.

        Args:
            jwt_token: Optional JWT token. If not provided, will be obtained
                from the nigel authentication daemon when needed.

        Environment Variables:
            DATASTORE_USE_INSECURE_CHANNEL: Set to 'true', '1', or 'yes' to force
                insecure channels for all targets. This is useful when connecting
                to datastore instances on private networks where TLS is not configured.
                Default: not set (secure channels used for non-local targets).

            DATASTORE_DISABLE_AUTH: Set to 'true', '1', or 'yes' to disable authentication
                entirely and use GrpcChannelPool instead of AuthGrpcChannelPool.
                Default: not set (authentication enabled).
                Note: Authentication is required for secure channels. Only use this with
                DATASTORE_USE_INSECURE_CHANNEL=true for local/testing scenarios.
        """
        super().__init__()
        self._jwt_token = jwt_token
        self._token_provider: Optional[JwtTokenProvider] = None

    def _create_channel(self, target: str) -> grpc.Channel:
        options = [
            ("grpc.max_receive_message_length", -1),
            ("grpc.max_send_message_length", -1),
        ]

        # Check environment variable first for explicit override
        use_insecure = os.environ.get("DATASTORE_USE_INSECURE_CHANNEL", "").lower() in (
            "true",
            "1",
            "yes",
        )

        if use_insecure or self._is_local(target):
            if use_insecure:
                _logger.info(
                    f"Using insecure channel for {target} (DATASTORE_USE_INSECURE_CHANNEL is set)"
                )
            else:
                _logger.debug(f"Using insecure channel for local target: {target}")

            options.append(("grpc.enable_http_proxy", 0))
            channel = grpc.insecure_channel(target, options)
        else:
            _logger.debug(f"Using secure channel with SSL for target: {target}")

            credentials = grpc.ssl_channel_credentials()
            channel = grpc.secure_channel(target, credentials, options)

        # Get JWT token (from parameter or auth daemon)
        try:
            # Create token provider if we have a static token
            if self._jwt_token and self._token_provider is None:
                # Create a simple provider that returns the static token
                self._token_provider = JwtTokenProvider(grpc_channel_pool=self)
                self._token_provider._cached_token = self._jwt_token

            token_provider = self._get_token_provider()
            return grpc.intercept_channel(channel, _AuthInterceptor(token_provider))
        except Exception as e:
            _logger.warning(f"Failed to obtain JWT token, proceeding without auth: {e}")

        return channel

    def _get_token_provider(self) -> JwtTokenProvider:
        """Get the JWT token provider, creating it if needed.

        Returns:
            The JwtTokenProvider instance.
        """
        if self._token_provider is None:
            self._token_provider = JwtTokenProvider(grpc_channel_pool=self)
        return self._token_provider
