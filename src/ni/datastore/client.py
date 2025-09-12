from datetime import datetime, timezone
from typing import Union

from google.protobuf.timestamp_pb2 import Timestamp
from nitypes.waveform import AnalogWaveform, DigitalWaveform
from ni.datastore.placeholder_types import MetadataStoreClient, MonikerClient
from ni.datastore.types import (
      StoredDataValue, Measurement, PassFailStatus, Moniker
)
from ni.measurements.data.v1.data_store_pb2 import PublishableData, PassFailStatus, ErrorState
from ni.measurements.data.v1.data_store_service_pb2 import PublishDataRequest, PublishDataResponse
from ni.measurements.data.v1.client import DataStoreClient


class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = ("_data_store_client", "_metadata_store_client", "_moniker_client")

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient
    _moniker_client: MonikerClient

    def __init__(self):
        self._data_store_client = DataStoreClient()

    def publish_bool(self):
        publishable_data = PublishableData()
        publishable_data.scalar.bool_value = True
        self._publish_data(
            publishable_data,
            "Simple Boolean",
            measurement_id=""
        )
        pass

    def publish_data(
            self,
            name: str,
            value: Union[str, bool, int, float, AnalogWaveform, DigitalWaveform],
            description: str,
            passFailStatus: PassFailStatus,
            measurement: Measurement,
        ) -> StoredDataValue:
            """Publish a polymorphic data value to the datastore.

                * Open Question: Should this be a general 'publish_data'?
                * Where do we put the data, metadata, etc client stubs?
            """
            if isinstance(value, (AnalogWaveform)):
                pass
            return StoredDataValue()
    
    def read_data(
            self,
            moniker: Moniker,
        ) -> Union[str, bool, int, float]:
            """Read a scalar value from the datastore."""
            return True


    def _publish_data(
        self,
        data: PublishableData,
        description: str,
        measurement_id: str
    ) -> PublishDataResponse:
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
        return publish_response
