"""Error Information data type for the Data Store Client."""

from __future__ import annotations

from ni.measurements.data.v1.data_store_pb2 import (
    ErrorInformation as ErrorInformationProto,
)


class ErrorInformation:
    """Represents error or exception information in case of measurement failure.

    An ErrorInformation contains an error code, descriptive message, and
    source information to help identify and diagnose issues during measurement
    execution.
    """

    __slots__ = (
        "error_code",
        "message",
        "source",
    )

    def __init__(
        self,
        *,
        error_code: int = 0,
        message: str = "",
        source: str = "",
    ) -> None:
        """Initialize an ErrorInformation instance.

        Args:
            error_code: The numeric error code associated with the error.
            message: A descriptive message explaining the error.
            source: The source or location where the error occurred.
        """
        self.error_code = error_code
        self.message = message
        self.source = source

    @staticmethod
    def from_protobuf(
        error_information_proto: ErrorInformationProto,
    ) -> "ErrorInformation":
        """Create an ErrorInformation instance from a protobuf ErrorInformation message."""
        return ErrorInformation(
            error_code=error_information_proto.error_code,
            message=error_information_proto.message,
            source=error_information_proto.source,
        )

    def to_protobuf(self) -> ErrorInformationProto:
        """Convert this ErrorInformation instance to a protobuf ErrorInformation message."""
        return ErrorInformationProto(
            error_code=self.error_code,
            message=self.message,
            source=self.source,
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, ErrorInformation):
            return NotImplemented
        return (
            self.error_code == other.error_code
            and self.message == other.message
            and self.source == other.source
        )

    def __str__(self) -> str:
        """Return a string representation of the ErrorInformation."""
        return str(self.to_protobuf())
