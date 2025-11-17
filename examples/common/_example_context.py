import os
import sys

from pathlib import Path
from types import TracebackType

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ni.measurementlink.discovery.v1.client import DiscoveryClient

DATA_STORE_SERVICE_INTERFACE = "ni.measurements.data.v1.DataStoreService"

DISCOVERY_SERVICE_CLUSTER_ID_ENV_VAR = "NIDiscovery_ClusterId"
EXAMPLES_DISCOVERY_SERVICE_CLUSTER_ID = "ac0fe6b9-91a9-4cb2-ba3e-0c88f108524f"

# Environment variables controlling files created or used by the Data Store service
DATA_STORE_DATABASE_PATH_ENV_VAR = "DataStoreSettings__SqliteDatabasePath"
DATA_STORE_DATA_FILES_DIRECTORY_PATH_ENV_VAR = "DataStoreSettings__DataFilesDirectory"
DATA_STORE_INGEST_DIRECTORY_PATH_ENV_VAR = "DataStoreSettings__IngestDirectory"
DATA_STORE_FAILED_INGEST_DIRECTORY_PATH_ENV_VAR = "DataStoreSettings__FailedIngestDirectory"
DATA_STORE_TDMS_EXPIRATION_SECONDS_ENV_NAME = "DataStoreSettings__TdmsFileCacheExpirationSeconds"

class ExampleContext:
    __slots__ = ("_discovery_client")

    def __init__(self):
        self._discovery_client: DiscoveryClient | None = None


    def __enter__(self) -> Self:
        self.initialize()
        return self


    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
       self.close()


    def initialize(self) -> None:
        if self._discovery_client is None:
            self._initialize_environment()

            self._discovery_client = DiscoveryClient()
            # Ensure the Discovery Service is launched by resolving a service
            self._discovery_client.resolve_service(provided_interface=DATA_STORE_SERVICE_INTERFACE)


    def close(self) -> None:
        if self._discovery_client is not None:
            self._discovery_client.stop_launched_discovery_service()
            self._discovery_client = None

            self._reset_environment()


    def _initialize_environment(self) -> None:
        example_data_directory = self._ensure_example_data_directory_exists()

        metadata_db_path = example_data_directory / "MetadataStore.db"
        data_files_dir = example_data_directory / "Data Files"
        ingest_dir = example_data_directory / "Ingest"
        failed_ingest_dir = example_data_directory / "Failed Ingest"

        data_files_dir.mkdir(exist_ok=True)
        ingest_dir.mkdir(exist_ok=True)
        failed_ingest_dir.mkdir(exist_ok=True)

        # Ensure that the Discovery Service that we launch is specific to the execution of these examples
        os.environ[DISCOVERY_SERVICE_CLUSTER_ID_ENV_VAR] = EXAMPLES_DISCOVERY_SERVICE_CLUSTER_ID

        os.environ[DATA_STORE_DATABASE_PATH_ENV_VAR] = str(metadata_db_path)
        os.environ[DATA_STORE_DATA_FILES_DIRECTORY_PATH_ENV_VAR] = str(data_files_dir)
        os.environ[DATA_STORE_INGEST_DIRECTORY_PATH_ENV_VAR] = str(ingest_dir)
        os.environ[DATA_STORE_FAILED_INGEST_DIRECTORY_PATH_ENV_VAR] = str(failed_ingest_dir)
        os.environ[DATA_STORE_TDMS_EXPIRATION_SECONDS_ENV_NAME] = str(0)


    def _ensure_example_data_directory_exists(self) -> Path:
        examples_directory = Path(__file__).resolve().parents[1]
        example_data_directory = examples_directory / "example_data"
        example_data_directory.mkdir(exist_ok=True)
        return example_data_directory


    def _reset_environment(self) -> None:
        for env_var in [
            DISCOVERY_SERVICE_CLUSTER_ID_ENV_VAR,
            DATA_STORE_DATABASE_PATH_ENV_VAR,
            DATA_STORE_DATA_FILES_DIRECTORY_PATH_ENV_VAR,
            DATA_STORE_INGEST_DIRECTORY_PATH_ENV_VAR,
            DATA_STORE_FAILED_INGEST_DIRECTORY_PATH_ENV_VAR,
            DATA_STORE_TDMS_EXPIRATION_SECONDS_ENV_NAME,
        ]:
            if env_var in os.environ:
                del os.environ[env_var]
