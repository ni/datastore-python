"""Datastore client for publishing and reading data."""

from __future__ import annotations

from collections.abc import Iterable
from threading import Lock
from typing import Type, TypeVar, cast
from urllib.parse import urlparse

import numpy as np
from google.protobuf.any_pb2 import Any
from ni.datamonikers.v1.client import MonikerClient
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.client import DataStoreClient
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedCondition,
    PublishedMeasurement,
)
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)
from ni.measurements.metadata.v1.client import MetadataStoreClient
from ni.protobuf.types.precision_timestamp_conversion import (
    bintime_datetime_to_protobuf,
)
from ni.protobuf.types.scalar_conversion import scalar_to_protobuf
from ni.protobuf.types.vector_conversion import vector_from_protobuf, vector_to_protobuf
from ni.protobuf.types.vector_pb2 import Vector as VectorProto
from ni.protobuf.types.waveform_conversion import (
    digital_waveform_from_protobuf,
    digital_waveform_to_protobuf,
    float64_analog_waveform_from_protobuf,
    float64_analog_waveform_to_protobuf,
    float64_complex_waveform_from_protobuf,
    float64_complex_waveform_to_protobuf,
    float64_spectrum_from_protobuf,
    float64_spectrum_to_protobuf,
    int16_analog_waveform_from_protobuf,
    int16_analog_waveform_to_protobuf,
    int16_complex_waveform_from_protobuf,
    int16_complex_waveform_to_protobuf,
)
from ni.protobuf.types.waveform_pb2 import (
    DigitalWaveform as DigitalWaveformProto,
    DoubleAnalogWaveform,
    DoubleComplexWaveform,
    DoubleSpectrum,
    I16AnalogWaveform,
    I16ComplexWaveform,
)
from ni.protobuf.types.xydata_pb2 import DoubleXYData
from nitypes.bintime import DateTime
from nitypes.complex import ComplexInt32Base
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum

TRead = TypeVar("TRead")


class Client:
    """Datastore client for publishing and reading data."""

    __slots__ = (
        "_data_store_client",
        "_metadata_store_client",
        "_moniker_clients",
        "_moniker_clients_lock",
    )

    _data_store_client: DataStoreClient
    _metadata_store_client: MetadataStoreClient
    _moniker_clients: dict[str, MonikerClient]
    _moniker_clients_lock: Lock

    def __init__(
        self,
        data_store_client: DataStoreClient | None = None,
        metadata_store_client: MetadataStoreClient | None = None,
        moniker_clients: dict[str, MonikerClient] | None = None,
    ) -> None:
        """Initialize the Client."""
        self._data_store_client = data_store_client or DataStoreClient()
        self._metadata_store_client = metadata_store_client or MetadataStoreClient()
        self._moniker_clients = moniker_clients or {}
        self._moniker_clients_lock = Lock()

    def publish_condition(
        self,
        condition_name: str,
        type: str,
        value: object,
        step_id: str,
    ) -> PublishedCondition:
        """Publish a condition value to the data store."""
        publish_request = PublishConditionRequest(
            condition_name=condition_name,
            type=type,
            step_id=step_id,
        )
        self._populate_publish_condition_request_value(publish_request, value)
        publish_response = self._data_store_client.publish_condition(publish_request)
        return publish_response.published_condition

    def publish_condition_batch(
        self, condition_name: str, type: str, values: object, step_id: str
    ) -> PublishedCondition:
        """Publish a batch of N values for a condition to the data store."""
        publish_request = PublishConditionBatchRequest(
            condition_name=condition_name,
            type=type,
            step_id=step_id,
        )
        self._populate_publish_condition_batch_request_values(publish_request, values)
        publish_response = self._data_store_client.publish_condition_batch(publish_request)
        return publish_response.published_condition

    def publish_measurement(
        self,
        measurement_name: str,
        value: object,  # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        step_id: str,
        timestamp: DateTime,
        outcome: Outcome.ValueType | None = None,
        error_information: ErrorInformation | None = None,
        hardware_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
        notes: str | None = None,
    ) -> PublishedMeasurement:
        """Publish a measurement value to the data store."""
        if outcome is None:
            outcome = Outcome.OUTCOME_UNSPECIFIED

        if notes is None:
            notes = ""

        publish_request = PublishMeasurementRequest(
            measurement_name=measurement_name,
            step_id=step_id,
            timestamp=bintime_datetime_to_protobuf(timestamp),
            outcome=outcome,
            error_information=error_information,
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
            notes=notes,
        )
        self._populate_publish_measurement_request_value(publish_request, value)
        publish_response = self._data_store_client.publish_measurement(publish_request)
        return publish_response.published_measurement

    def publish_measurement_batch(
        self,
        measurement_name: str,
        values: object,
        step_id: str,
        timestamps: Iterable[DateTime] = tuple(),
        outcomes: Iterable[Outcome.ValueType] = tuple(),
        error_information: Iterable[ErrorInformation] = tuple(),
        hardware_item_ids: Iterable[str] = tuple(),
        test_adapter_ids: Iterable[str] = tuple(),
        software_item_ids: Iterable[str] = tuple(),
    ) -> Iterable[PublishedMeasurement]:
        """Publish a batch of N values of a measurement to the data store."""
        publish_request = PublishMeasurementBatchRequest(
            measurement_name=measurement_name,
            step_id=step_id,
            timestamp=[bintime_datetime_to_protobuf(ts) for ts in timestamps],
            outcome=outcomes,
            error_information=list(error_information),
            hardware_item_ids=hardware_item_ids,
            test_adapter_ids=test_adapter_ids,
            software_item_ids=software_item_ids,
        )
        self._populate_publish_measurement_batch_request_values(publish_request, values)
        publish_response = self._data_store_client.publish_measurement_batch(publish_request)
        return publish_response.published_measurements

    def read(
        self,
        moniker_source: Moniker | PublishedMeasurement | PublishedCondition,
        expected_type: Type[TRead],
    ) -> TRead:
        """Read data published to the data store."""
        if isinstance(moniker_source, Moniker):
            moniker = moniker_source
        elif isinstance(moniker_source, PublishedMeasurement):
            moniker = moniker_source.moniker
        elif isinstance(moniker_source, PublishedCondition):
            moniker = moniker_source.moniker

        moniker_client = self._get_moniker_client(moniker.service_location)
        read_result = moniker_client.read_from_moniker(moniker)

        unpacked_data = self._unpack_data(read_result.value)
        converted_data = self._convert_from_protobuf(unpacked_data)
        if not isinstance(converted_data, expected_type):
            raise TypeError(f"Expected type {expected_type}, got {type(converted_data)}")
        return converted_data

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

    def _get_moniker_client(self, service_location: str) -> MonikerClient:
        parsed_location = urlparse(service_location).netloc

        with self._moniker_clients_lock:
            if parsed_location not in self._moniker_clients:
                self._moniker_clients[parsed_location] = MonikerClient(
                    service_location=parsed_location
                )
            return self._moniker_clients[parsed_location]

    # TODO: We may wish to separate out some of the conversion code below.
    def _populate_publish_condition_request_value(
        self, publish_request: PublishConditionRequest, value: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as float
        # TODO: or require wrapping in a Scalar.
        if isinstance(value, bool):
            publish_request.scalar.bool_value = value
        elif isinstance(value, int):
            publish_request.scalar.sint32_value = value
        elif isinstance(value, float):
            publish_request.scalar.double_value = value
        elif isinstance(value, str):
            publish_request.scalar.string_value = value
        elif isinstance(value, Scalar):
            publish_request.scalar.CopyFrom(scalar_to_protobuf(value))
        else:
            raise TypeError(
                f"Unsupported condition value type: {type(value)}. Please consult the docummentation."
            )

    def _populate_publish_condition_batch_request_values(
        self, publish_request: PublishConditionBatchRequest, values: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as a list of float
        if isinstance(values, Vector):
            publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
        else:
            raise TypeError(
                f"Unsupported condition values type: {type(values)}. Please consult the docummentation."
            )

    def _populate_publish_measurement_request_value(
        self, publish_request: PublishMeasurementRequest, value: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as float
        # TODO: or require wrapping in a Scalar.
        if isinstance(value, bool):
            publish_request.scalar.bool_value = value
        elif isinstance(value, int):
            publish_request.scalar.sint32_value = value
        elif isinstance(value, float):
            publish_request.scalar.double_value = value
        elif isinstance(value, str):
            publish_request.scalar.string_value = value
        elif isinstance(value, Scalar):
            publish_request.scalar.CopyFrom(scalar_to_protobuf(value))
        elif isinstance(value, Vector):
            publish_request.vector.CopyFrom(vector_to_protobuf(value))
        elif isinstance(value, AnalogWaveform):
            analog_waveform = cast(AnalogWaveform, value)
            if analog_waveform.dtype == np.float64:
                publish_request.double_analog_waveform.CopyFrom(
                    float64_analog_waveform_to_protobuf(analog_waveform)
                )
            elif analog_waveform.dtype == np.int16:
                publish_request.i16_analog_waveform.CopyFrom(
                    int16_analog_waveform_to_protobuf(analog_waveform)
                )
            else:
                raise TypeError(f"Unsupported AnalogWaveform dtype: {analog_waveform.dtype}")
        elif isinstance(value, ComplexWaveform):
            complex_waveform = cast(ComplexWaveform, value)
            if complex_waveform.dtype == np.complex128:
                publish_request.double_complex_waveform.CopyFrom(
                    float64_complex_waveform_to_protobuf(complex_waveform)
                )
            elif complex_waveform.dtype == ComplexInt32Base:
                publish_request.i16_complex_waveform.CopyFrom(
                    int16_complex_waveform_to_protobuf(complex_waveform)
                )
            else:
                raise TypeError(f"Unsupported ComplexWaveform dtype: {complex_waveform.dtype}")
        elif isinstance(value, Spectrum):
            spectrum = cast(Spectrum, value)
            if spectrum.dtype == np.float64:
                publish_request.double_spectrum.CopyFrom(float64_spectrum_to_protobuf(spectrum))
            else:
                raise TypeError(f"Unsupported Spectrum dtype: {spectrum.dtype}")
        elif isinstance(value, DigitalWaveform):
            publish_request.digital_waveform.CopyFrom(digital_waveform_to_protobuf(value))
        else:
            raise TypeError(
                f"Unsupported measurement value type: {type(value)}. Please consult the docummentation."
            )
        # TODO: Implement conversion from proper XYData type

    def _populate_publish_measurement_batch_request_values(
        self, publish_request: PublishMeasurementBatchRequest, values: object
    ) -> None:
        # TODO: Determine whether we wish to support primitive types such as a list of float
        if isinstance(values, Vector):
            publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
        else:
            raise TypeError(
                f"Unsupported measurement values type: {type(values)}. Please consult the docummentation."
            )

    def _unpack_data(self, read_value: Any) -> object:
        data_type_url = read_value.type_url

        data_type_prefix = "type.googleapis.com/"
        if data_type_url == data_type_prefix + DoubleAnalogWaveform.DESCRIPTOR.full_name:
            waveform = DoubleAnalogWaveform()
            read_value.Unpack(waveform)
            return waveform
        elif data_type_url == data_type_prefix + I16AnalogWaveform.DESCRIPTOR.full_name:
            waveform = I16AnalogWaveform()
            read_value.Unpack(waveform)
            return waveform
        elif data_type_url == data_type_prefix + DoubleComplexWaveform.DESCRIPTOR.full_name:
            waveform = DoubleComplexWaveform()
            read_value.Unpack(waveform)
            return waveform
        elif data_type_url == data_type_prefix + I16ComplexWaveform.DESCRIPTOR.full_name:
            waveform = I16ComplexWaveform()
            read_value.Unpack(waveform)
            return waveform
        elif data_type_url == data_type_prefix + DoubleSpectrum.DESCRIPTOR.full_name:
            spectrum = DoubleSpectrum()
            read_value.Unpack(spectrum)
            return spectrum
        elif data_type_url == data_type_prefix + DigitalWaveformProto.DESCRIPTOR.full_name:
            waveform = DigitalWaveformProto()
            read_value.Unpack(waveform)
            return waveform
        elif data_type_url == data_type_prefix + DoubleXYData.DESCRIPTOR.full_name:
            xydata = DoubleXYData()
            read_value.Unpack(xydata)
            return xydata
        elif data_type_url == data_type_prefix + VectorProto.DESCRIPTOR.full_name:
            vector = VectorProto()
            read_value.Unpack(vector)
            return vector

        else:
            raise TypeError(f"Unsupported data type URL: {data_type_url}")

    def _convert_from_protobuf(self, unpacked_data: object) -> object:
        if isinstance(unpacked_data, DoubleAnalogWaveform):
            return float64_analog_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, I16AnalogWaveform):
            return int16_analog_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DoubleComplexWaveform):
            return float64_complex_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, I16ComplexWaveform):
            return int16_complex_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DoubleSpectrum):
            return float64_spectrum_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DigitalWaveformProto):
            return digital_waveform_from_protobuf(unpacked_data)
        elif isinstance(unpacked_data, DoubleXYData):
            return unpacked_data  # TODO: Implement conversion to proper XYData type
        elif isinstance(unpacked_data, VectorProto):
            return vector_from_protobuf(unpacked_data)
        else:
            raise TypeError(f"Unsupported unpacked data type: {type(unpacked_data)}")
