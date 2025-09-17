"""Datastore client for publishing and reading data."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Type, TypeVar, cast

import numpy as np
from ni.datamonikers.v1.client import MonikerClient
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
from ni.protobuf.types.waveform_conversion import float64_analog_waveform_to_protobuf
from nitypes.bintime import DateTime
from nitypes.waveform import AnalogWaveform

TRead = TypeVar("TRead")
TWrite = TypeVar("TWrite")


class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = ("_data_store_client", "_metadata_store_client", "_moniker_client")

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient
    _moniker_client: MonikerClient

    def __init__(
        self,
        data_store_client: DataStoreClient | None = None,
        metadata_store_client: MetadataStoreClient | None = None,
        moniker_client: MonikerClient | None = None,
    ) -> None:
        """Initialize the Client."""
        self._data_store_client = data_store_client or DataStoreClient()
        self._metadata_store_client = metadata_store_client or MetadataStoreClient()
        self._moniker_client = moniker_client or MonikerClient(service_location="dummy")

    def publish_measurement_data(
        self,
        step_id: str,
        name: str,
        notes: str,
        timestamp: DateTime,
        data: object,  # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        outcome: Outcome.ValueType,
        error_info: ErrorInformation,
        hardware_item_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
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
        elif isinstance(data, AnalogWaveform):
            # Assuming data is of type AnalogWaveform
            analog_waveform = cast(AnalogWaveform[np.float64], data)
            publish_request.double_analog_waveform.CopyFrom(
                float64_analog_waveform_to_protobuf(analog_waveform)
            )

        publish_response = self._data_store_client.publish_measurement(publish_request)
        return publish_response.published_measurement

    def read_measurement_data(
        self, moniker_source: Moniker | PublishedMeasurement, expected_type: Type[TRead]
    ) -> TRead:
        """Read measurement data from the datastore."""
        if isinstance(moniker_source, Moniker):
            moniker = moniker_source
        else:
            moniker = moniker_source.moniker
        self._moniker_client._service_location = moniker.service_location
        result = self._moniker_client.read_from_moniker(moniker)
        if not isinstance(result.value, expected_type):
            raise TypeError(f"Expected type {expected_type}, got {type(result.value)}")
        return result.value

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
