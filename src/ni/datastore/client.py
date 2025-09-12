from datetime import datetime, timezone
from typing import Union

from google.protobuf.timestamp_pb2 import Timestamp
from nitypes.waveform import AnalogWaveform, DigitalWaveform
from ni.datamonikers.v1.client import MonikerClient
from ni.datastore.types import (
      StoredDataValue,
      Measurement,
      PassFailStatus,
      Moniker
)
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorState,
    MeasurementMetadata,
    PassFailStatus,
    PublishableData,
    StoredDataValue,
)
from ni.measurements.data.v1.data_store_service_pb2 import PublishDataRequest, PublishDataResponse, CreateMeasurementRequest
from ni.measurements.data.v1.client import DataStoreClient
from ni.measurements.metadata.v1.client import MetadataStoreClient
from ni.protobuf.types.vector_pb2 import Vector

class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = ("_data_store_client", "_metadata_store_client", "_moniker_client")

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient

    def __init__(self):
        self._data_store_client = DataStoreClient()
        self._metadata_store_client = MetadataStoreClient()

    def publish_bool(self, value: bool) -> StoredDataValue:
        publishable_data = PublishableData()
        publishable_data.scalar.bool_value = value
        create_measurement_request = CreateMeasurementRequest(measurement=MeasurementMetadata(name="Boolean Measurement"))
        measurement_id = self._data_store_client.create_measurement(create_measurement_request).id
        return self._publish_data(
            publishable_data,
            "Simple Boolean",
            measurement_id=measurement_id
        )

    def read_bool(self, stored_data_value: StoredDataValue) -> bool:
        moniker = stored_data_value.moniker
        moniker_client = MonikerClient(service_location='localhost:53361')
        result = moniker_client.read_from_moniker(moniker)
        vector = Vector()
        result.value.Unpack(vector)
        return vector.bool_array.values[0]

    def _publish_data(
        self,
        data: PublishableData,
        description: str,
        measurement_id: str
    ) -> StoredDataValue:
        timestamp = datetime.now(timezone.utc)
        request_timestamp = Timestamp()
        request_timestamp.FromDatetime(timestamp)
        publish_request = PublishDataRequest(
            notes=description,
            data=data,
            timestamp=request_timestamp,
            pass_fail_status=PassFailStatus.PASS_FAIL_STATUS_FAILED,
            error_state=ErrorState.ERROR_STATE_NO_ERROR,
            measurement_id=measurement_id
        )

        publish_response = self._data_store_client.publish_data(publish_request)
        return publish_response.stored_data_value
