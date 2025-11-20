import hashlib
import os
import sys
from pathlib import Path
from types import TracebackType

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

DISCOVERY_SERVICE_CLUSTER_ID_ENV_VAR = "NIDiscovery_ClusterId"

# Environment variables controlling files created or used by the Data Store service
DATA_STORE_DATABASE_PATH_ENV_VAR = "DataStoreSettings__SqliteDatabasePath"
DATA_STORE_DATA_FILES_DIRECTORY_PATH_ENV_VAR = "DataStoreSettings__DataFilesDirectory"
DATA_STORE_INGEST_DIRECTORY_PATH_ENV_VAR = "DataStoreSettings__IngestDirectory"
DATA_STORE_FAILED_INGEST_DIRECTORY_PATH_ENV_VAR = "DataStoreSettings__FailedIngestDirectory"
DATA_STORE_TDMS_EXPIRATION_SECONDS_ENV_NAME = "DataStoreSettings__TdmsFileCacheExpirationSeconds"

DEFAULT_FOLDER_NAME = "temp_data"


class DataStoreContext:
    """A context manager for running a data store in an isolated environment."""

    __slots__ = "_base_directory_path", "_original_environment"

    def __init__(self, base_directory_path: Path | None = None) -> None:
        """Initialize the DataStoreContext.

        Args:
            base_directory_path: An optional base directory path specifying where
            the data store files will be located. If not provided, a default path
            in the repository directory will be used.
        """
        self._base_directory_path = base_directory_path
        self._original_environment = {}

    def __enter__(self) -> Self:
        """Enter the data store context."""
        self.initialize()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the data store context."""
        self.close()

    def initialize(self) -> None:
        """Initializes the data store context by setting up necessary environment variables."""
        self._initialize_environment()

    def close(self) -> None:
        """Cleans up the data store context by resetting environment variables."""
        self._restore_environment()

    def _initialize_environment(self) -> None:
        self._save_original_environment()
        self._initialize_cluster_id()
        self._initialize_data_store_paths()

    def _save_original_environment(self) -> None:
        # Save the original values (or None if not set)
        for environment_variable in [
            DISCOVERY_SERVICE_CLUSTER_ID_ENV_VAR,
            DATA_STORE_DATABASE_PATH_ENV_VAR,
            DATA_STORE_DATA_FILES_DIRECTORY_PATH_ENV_VAR,
            DATA_STORE_INGEST_DIRECTORY_PATH_ENV_VAR,
            DATA_STORE_FAILED_INGEST_DIRECTORY_PATH_ENV_VAR,
            DATA_STORE_TDMS_EXPIRATION_SECONDS_ENV_NAME,
        ]:
            self._original_environment[environment_variable] = os.environ.get(environment_variable)

    def _initialize_cluster_id(self) -> None:
        cluster_id = self._get_cluster_id()
        os.environ[DISCOVERY_SERVICE_CLUSTER_ID_ENV_VAR] = cluster_id

    def _initialize_data_store_paths(self) -> None:
        base_directory_path = self._get_base_directory_path()

        metadata_db_path = base_directory_path / "MetadataStore.db"
        data_files_dir = base_directory_path / "DataFiles"
        ingest_dir = base_directory_path / "Ingest"
        failed_ingest_dir = base_directory_path / "FailedIngest"

        os.environ[DATA_STORE_DATABASE_PATH_ENV_VAR] = str(metadata_db_path)
        os.environ[DATA_STORE_DATA_FILES_DIRECTORY_PATH_ENV_VAR] = str(data_files_dir)
        os.environ[DATA_STORE_INGEST_DIRECTORY_PATH_ENV_VAR] = str(ingest_dir)
        os.environ[DATA_STORE_FAILED_INGEST_DIRECTORY_PATH_ENV_VAR] = str(failed_ingest_dir)

        os.environ[DATA_STORE_TDMS_EXPIRATION_SECONDS_ENV_NAME] = str(0)

    def _get_cluster_id(self) -> str:
        # Generate a unique cluster ID based on the base directory path
        return self._get_base_directory_hash()

    def _get_base_directory_hash(self) -> str:
        base_directory_path = self._get_base_directory_path()
        base_directory_path_bytes = str(base_directory_path.resolve()).encode("utf-8")
        hash_object = hashlib.sha256(base_directory_path_bytes)
        return hash_object.hexdigest()[:32]

    def _get_base_directory_path(self) -> Path:
        if self._base_directory_path is not None:
            return self._base_directory_path

        repo_root = Path(__file__).resolve().parents[3]
        return repo_root / DEFAULT_FOLDER_NAME

    def _restore_environment(self) -> None:
        for environment_variable, original_value in self._original_environment.items():
            if original_value is None:
                # The environment variable was not originally set; remove it
                if environment_variable in os.environ:
                    del os.environ[environment_variable]
            else:
                # Restore the original value
                os.environ[environment_variable] = original_value
