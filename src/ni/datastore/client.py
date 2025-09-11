from typing import Union

from nitypes.waveform import AnalogWaveform, DigitalWaveform
from ni.datastore.placeholder_types import MetadataStoreClient, DataStoreClient, MonikerClient
from ni.datastore.types import (
      StoredDataValue, Measurement, PassFailStatus, Moniker
)


class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = ("_data_store_client", "_metadata_store_client", "_moniker_client")

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient
    _moniker_client: MonikerClient

    def __init__(self):
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