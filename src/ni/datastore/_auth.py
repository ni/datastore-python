import base64
import collections
import json
import logging
import os
import platform
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
    def __init__(self, token):
        self._token = token

    def _add_auth_metadata(self, client_call_details):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append(("authorization", f"Bearer {self._token}"))

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

        First attempts to use the NIGEL_SERVICES_JWT_TOKEN environment variable.
        Then tries to get the token via the nigel CLI executable.
        In the future, will use gRPC to communicate with the auth daemon directly.

        Returns:
            The JWT token string.

        Raises:
            RuntimeError: If unable to obtain the JWT token.
        """
        # Check for environment variable override first (for testing)
        env_token = os.environ.get("NIGEL_SERVICES_JWT_TOKEN")
        if env_token:
            _logger.debug("Using JWT token from NIGEL_SERVICES_JWT_TOKEN environment variable")
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

        # TODO: Replace CLI-based approach with gRPC once proto definitions are available
        # The gRPC approach is preferred for production use as it's more efficient
        # and doesn't require spawning a subprocess.
        #
        # To implement the gRPC approach:
        #
        # 1. Add the nigel auth service proto package as a dependency in pyproject.toml
        #    Example: ni-testhub-auth-v1-client = "^1.0.0"
        #
        # 2. Import and use the auth service stubs:
        #    from ni.testhub.auth.v1 import auth_service_pb2, auth_service_pb2_grpc
        #
        # 3. Create the stub and make the gRPC call:
        #    auth_daemon_address = self._get_auth_daemon_address()
        #    channel = self._grpc_channel_pool.get_channel(auth_daemon_address)
        #    stub = auth_service_pb2_grpc.AuthServiceStub(channel)
        #    request = auth_service_pb2.GetTokenRequest()
        #    response = stub.GetToken(request)
        #    self._cached_token = response.token
        #    return self._cached_token
        #
        # 4. Verify the provided_interface and service_class in _resolve_auth_daemon_via_discovery
        #    match the actual values used by the nigel auth daemon
        #
        # For reference, see the daemon documentation at:
        # https://github.com/ni/testhub/blob/main/src/cli/docs/daemon.md

        raise RuntimeError(
            "Unable to obtain JWT token. Tried:\n"
            "1. NIGEL_SERVICES_JWT_TOKEN environment variable (not set)\n"
            f"2. nigel CLI executable ({'found' if nigel_path else 'not found'})\n"
            "3. gRPC auth daemon (not yet implemented)\n\n"
            "To resolve:\n"
            "- Set NIGEL_SERVICES_JWT_TOKEN environment variable with a valid token, or\n"
            "- Install the nigel CLI and ensure it's in your PATH or set NIGEL_CLI_PATH, or\n"
            "- Contact the development team to add gRPC proto definitions"
        )

    @staticmethod
    def _find_nigel_executable() -> Optional[str]:
        """Find the nigel CLI executable on the system.

        Searches for the nigel executable in the following order:
        1. NIGEL_CLI_PATH environment variable (if set)
        2. System PATH
        3. Platform-specific default installation paths

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

        # Platform-specific default paths
        system = platform.system()
        search_paths = []

        if system == "Windows":
            localappdata = os.environ.get("LOCALAPPDATA", "")
            if localappdata:
                search_paths.append(Path(localappdata) / "nigel" / "nigel.exe")
        elif system == "Linux":
            home = Path.home()
            search_paths.extend(
                [
                    home / ".local" / "bin" / "nigel",
                    home / "bin" / "nigel",
                    home / "opt" / "nigel" / "bin" / "nigel",
                ]
            )
        elif system == "Darwin":  # macOS
            search_paths.extend(
                [
                    Path("/usr/local/bin/nigel"),
                    Path.home() / ".local" / "bin" / "nigel",
                ]
            )

        # Search in platform-specific paths
        for path in search_paths:
            if path.exists() and path.is_file():
                _logger.debug(f"Found nigel at: {path}")
                return str(path)

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
                _logger.debug(f"Token expired or expiring soon (exp: {exp}, current: {current_time})")
                return True

            return False

        except Exception as e:
            _logger.warning(f"Error checking token expiration: {e}")
            return True  # Treat any errors as expired for safety

    def _get_auth_daemon_address(self) -> str:
        """Get the address of the nigel authentication daemon.

        On Windows, uses the discovery service to resolve the daemon.
        On other platforms, uses the NIGEL_SERVICES_AUTH_PORT environment variable
        with localhost.

        Returns:
            The address of the auth daemon (host:port).

        Raises:
            RuntimeError: If unable to determine the auth daemon address.
        """
        system = platform.system()

        if system == "Windows":
            return self._resolve_auth_daemon_via_discovery()
        else:
            # Linux/Mac: Use environment variable
            port = os.environ.get("NIGEL_SERVICES_AUTH_PORT")
            if not port:
                raise RuntimeError(
                    "NIGEL_SERVICES_AUTH_PORT environment variable not set. "
                    "This is required on non-Windows platforms."
                )
            return f"localhost:{port}"

    def _resolve_auth_daemon_via_discovery(self) -> str:
        """Resolve the auth daemon address using the discovery service (Windows only).

        Returns:
            The address of the auth daemon (host:port).

        Raises:
            RuntimeError: If unable to resolve the auth daemon.
        """
        try:
            from ni.measurementlink.discovery.v1.client import DiscoveryClient

            discovery_client = DiscoveryClient(grpc_channel_pool=self._grpc_channel_pool)

            # Resolve the auth service using discovery
            # These values should match the nigel auth daemon's registration
            service_location = discovery_client.resolve_service(
                provided_interface="ni.nigel.auth.v1.AuthService",
                service_class="ni.nigel.auth.daemon.v1",
            )

            # Prefer insecure port for local communication
            if service_location.insecure_port:
                return f"{service_location.location}:{service_location.insecure_port}"
            elif service_location.ssl_authenticated_port:
                return f"{service_location.location}:{service_location.ssl_authenticated_port}"
            else:
                raise RuntimeError("Auth daemon has no available ports")

        except ImportError as e:
            _logger.error("ni.measurementlink.discovery.v1.client not available")
            raise RuntimeError(
                "Discovery client not available. "
                "Please install ni-measurementlink-discovery-v1-client."
            ) from e
        except Exception as e:
            _logger.error(f"Failed to resolve auth daemon via discovery: {e}")
            raise RuntimeError(f"Unable to resolve auth daemon address: {e}") from e


class AuthGrpcChannelPool(GrpcChannelPool):
    def __init__(self, jwt_token: Optional[str] = None) -> None:
        """Initialize the authenticated gRPC channel pool.

        Args:
            jwt_token: Optional JWT token. If not provided, will be obtained
                from the nigel authentication daemon when needed.
        """
        super().__init__()
        self._jwt_token = jwt_token
        self._token_provider: Optional[JwtTokenProvider] = None

    def _get_jwt_token(self) -> str:
        """Get the JWT token, obtaining it from the auth daemon if needed.

        Returns:
            The JWT token string.
        """
        if self._jwt_token:
            return self._jwt_token

        if self._token_provider is None:
            self._token_provider = JwtTokenProvider(grpc_channel_pool=self)

        return self._token_provider.get_token()

    def _create_channel(self, target: str) -> grpc.Channel:
        options = [
            ("grpc.max_receive_message_length", -1),
            ("grpc.max_send_message_length", -1),
        ]
        if self._is_local(target):
            options.append(("grpc.enable_http_proxy", 0))
            channel = grpc.insecure_channel(target, options)
        else:
            credentials = grpc.ssl_channel_credentials()
            channel = grpc.secure_channel(target, credentials, options)

        # Get JWT token (from parameter or auth daemon)
        try:
            token = self._get_jwt_token()
            if token:
                return grpc.intercept_channel(channel, _AuthInterceptor(token))
        except Exception as e:
            _logger.warning(f"Failed to obtain JWT token, proceeding without auth: {e}")

        return channel


def get_jwt_token(grpc_channel_pool: Optional[GrpcChannelPool] = None) -> str:
    """Get a JWT token from the nigel authentication daemon.

    This is a convenience function that creates a JwtTokenProvider and retrieves a token.

    On Windows, uses the discovery service to resolve the daemon address.
    On Linux/Mac, uses the NIGEL_SERVICES_AUTH_PORT environment variable.

    The NIGEL_SERVICES_JWT_TOKEN environment variable can be set to override
    token retrieval for testing purposes.

    Args:
        grpc_channel_pool: Optional gRPC channel pool for making requests.
            If not provided, a new one will be created.

    Returns:
        The JWT token string.

    Raises:
        RuntimeError: If unable to obtain the JWT token.

    Example:
        >>> from ni.datastore._auth import get_jwt_token
        >>> token = get_jwt_token()
        >>> print(f"Token: {token[:20]}...")  # Print first 20 chars
    """
    provider = JwtTokenProvider(grpc_channel_pool)
    return provider.get_token()
