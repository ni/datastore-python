from nitypes.bintime import DateTime
from ni.datamonikers.v1.data_moniker_pb2 import Moniker
from ni.measurements.data.v1.data_store_pb2 import PublishedMeasurement, Outcome, ErrorInformation

class Client:
    """Datastore client for publishing and reading data."""

    def __init__(self):
        pass

    def publish_measurement_data(
        self,
        step_id: str,
        name: str,
        notes: str,
        timestamp: DateTime,
        data: object, # More strongly typed Union[bool, AnalogWaveform] can be used if needed
        outcome: Outcome,
        error_info: ErrorInformation,
        hardware_item_ids: list[str],
        software_item_ids: list[str],
        test_adapter_ids: list[str]
    ) -> PublishedMeasurement:
        return PublishedMeasurement()

    def read_measurement_data(self, moniker: Moniker) -> object: # What type is this object?
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
        return "test_result_id"