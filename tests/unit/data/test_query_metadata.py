"""Contains tests to validate the query_* methods in the data store."""

from __future__ import annotations

import datetime as std_datetime
from typing import cast
from unittest.mock import NonCallableMock

from hightime import datetime
from ni.datastore.data import (
    DataStoreClient,
    Step,
)
from ni.measurements.data.v1.data_store_pb2 import Step as StepProto
from ni.measurements.data.v1.data_store_service_pb2 import (
    QueryStepsRequest,
    QueryStepsResponse,
)
from ni.protobuf.types.precision_timestamp_conversion import (
    hightime_datetime_to_protobuf,
)


def test___query_steps___calls_data_store_service_client(
    data_store_client: DataStoreClient,
    mocked_data_store_service_client: NonCallableMock,
) -> None:
    start_time = datetime.now(tz=std_datetime.timezone.utc)
    end_time = datetime.now(tz=std_datetime.timezone.utc)
    step = StepProto(
        id="step_id",
        parent_step_id="parent_step_id",
        test_result_id="test_result",
        test_id="test_id",
        step_name="step_name",
        step_type="step_type",
        notes="step_notes",
        start_date_time=hightime_datetime_to_protobuf(start_time),
        end_date_time=hightime_datetime_to_protobuf(end_time),
    )
    mocked_data_store_service_client.query_steps.return_value = QueryStepsResponse(steps=[step])

    result = data_store_client.query_steps(odata_query="request_query")

    args, __ = mocked_data_store_service_client.query_steps.call_args
    request = cast(QueryStepsRequest, args[0])
    assert request.odata_query == "request_query"
    assert list(result) == [Step.from_protobuf(step)]
