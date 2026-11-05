"""Status data type for the V2 Data Store Client."""

from __future__ import annotations

from enum import IntEnum

from ni.measurements.data.v2.data_store_pb2 import Status as StatusProto


class Status(IntEnum):
    """Represents lifecycle progress, independent of the terminal Outcome."""

    UNSPECIFIED = StatusProto.STATUS_UNSPECIFIED
    """The status is not specified."""

    NOT_STARTED = StatusProto.STATUS_NOT_STARTED
    """The operation has not started."""

    LOOPING = StatusProto.STATUS_LOOPING
    """The operation is looping."""

    RUNNING = StatusProto.STATUS_RUNNING
    """The operation is running."""

    WAITING = StatusProto.STATUS_WAITING
    """The operation is waiting."""

    DONE = StatusProto.STATUS_DONE
    """The operation is done."""

    @classmethod
    def from_protobuf(cls, status_proto: StatusProto.ValueType) -> "Status":
        """Create a Status from a protobuf Status value."""
        try:
            return cls(status_proto)
        except ValueError as e:
            raise ValueError(f"Unknown status value: {status_proto}") from e

    def to_protobuf(self) -> StatusProto.ValueType:
        """Convert this Status to a protobuf Status value."""
        return StatusProto.ValueType(self.value)
