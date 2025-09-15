"""Datastore client for publishing and reading data."""

from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation,
    Outcome,
    PublishedMeasurement,
)
from nitypes.bintime import DateTime


class Client:
    """Datastore client for publishing and reading data."""

    def __init__(self) -> None:
        """Initialize the Client."""
        pass

    def publish_measurement_data(
        self,
        step_id: str,
        name: str,
        notes: str,
        timestamp: DateTime,
        data: object,  # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        outcome: Outcome,
        error_info: ErrorInformation,
        hardware_item_ids: list[str],
        software_item_ids: list[str],
        test_adapter_ids: list[str],
    ) -> PublishedMeasurement:
        """Publish measurement data to the datastore."""
        return PublishedMeasurement()

    def read_measurement_data(self, moniker: Moniker) -> object:
        """Read measurement data from the datastore."""
        return True

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
