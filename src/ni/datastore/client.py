"""Datastore client for publishing and reading data."""

from typing import Optional, Type, TypeVar, cast

from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.client import DataStoreClient
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedMeasurement,
)
from ni.measurements.data.v1.data_store_service_pb2 import PublishMeasurementRequest
from ni.measurements.metadata.v1.client import MetadataStoreClient
from ni.protobuf.types.precision_timestamp_conversion import (
    bintime_datetime_to_protobuf,
)
from nitypes.bintime import DateTime

TRead = TypeVar("TRead")
TWrite = TypeVar("TWrite")

class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = ("_data_store_client", "_metadata_store_client", "_moniker_client")

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient

    def __init__(
        self,
        data_store_client: Optional[DataStoreClient] = None,
        metadata_store_client: Optional[MetadataStoreClient] = None,
    ) -> None:
        """Initialize the Client."""
        self._data_store_client = data_store_client or DataStoreClient()
        self._metadata_store_client = metadata_store_client or MetadataStoreClient()

    def publish_measurement_data(
        self,
        step_id: str,
        name: str,
        notes: str,
        timestamp: DateTime,
        data: object, # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        outcome: Outcome.ValueType,
        error_info: ErrorInformation,
        hardware_item_ids: list[str],
        software_item_ids: list[str],
        test_adapter_ids: list[str],
    ) -> PublishedMeasurement:
        """Publish measurement data to the datastore."""
        publish_request = PublishMeasurementRequest(
            step_id=step_id,
            measurement_name=name,
            notes=notes,
            timestamp=bintime_datetime_to_protobuf(timestamp),
            outcome=outcome,
            error_information=error_info,
            hardware_item_ids=hardware_item_ids,
            software_item_ids=software_item_ids,
            test_adapter_ids=test_adapter_ids,
        )

        if isinstance(data, bool):
            publish_request.scalar.bool_value = data

        publish_response = self._data_store_client.publish_measurement(publish_request)
        return publish_response.published_measurement

    def read_measurement_data(self, moniker: Moniker, expected_type: Type[TRead]) -> TRead:
        """Read measurement data from the datastore."""
        return cast(TRead, True)

    def create_step(
        self,
        step_name: str,
        step_type: str,
        notes: str,
        start_time: DateTime,
        end_time: DateTime,
        test_result_id: str = "",
    ) -> str:
        """Create a test step in the datastore."""
        return "step_id"

    def create_test_result(
        self,
        test_name: str,
        uut_instance_id: str = "",
        operator_id: str = "",
        test_station_id: str = "",
        test_description_id: str = "",
        software_item_ids: list[str] = [],
        hardware_item_ids: list[str] = [],
        test_adapter_ids: list[str] = [],
    ) -> str:
        """Create a test result in the datastore."""
        return "test_result_id"
