"""JSON value data type for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any, cast

from google.protobuf import json_format
from ni.measurements.data.v2.data_store_pb2 import JsonValue as JsonValueProto
from ni.protobuf.types.attribute_value_pb2 import AttributeValue

AttributeValueType = bool | int | float | str


class JsonValue:
    """Structured JSON used as a measurement value, limit, or condition value.

    A plain dictionary can be used instead when no attributes or schema are needed.
    """

    __slots__ = ("_value", "_attributes", "schema_id")

    @property
    def value(self) -> MutableMapping[str, Any]:
        """The JSON object."""
        return self._value

    @property
    def attributes(self) -> MutableMapping[str, AttributeValueType]:
        """Attributes that describe the JSON value."""
        return self._attributes

    def __init__(
        self,
        value: Mapping[str, Any],
        *,
        attributes: Mapping[str, AttributeValueType] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a JsonValue instance.

        Args:
            value: The JSON object.
            attributes (optional): Attributes that describe the JSON value.
            schema_id (optional): Schema for the JSON content. Reserved by the
                service for future support.
        """
        self._value: MutableMapping[str, Any] = dict(value)
        self._attributes: MutableMapping[str, AttributeValueType] = (
            dict(attributes) if attributes is not None else {}
        )
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(json_value_proto: JsonValueProto) -> "JsonValue":
        """Create a JsonValue instance from a protobuf JsonValue message."""
        return JsonValue(
            json_format.MessageToDict(json_value_proto.value),
            attributes={
                key: getattr(attribute, cast(str, attribute.WhichOneof("attribute")))
                for key, attribute in json_value_proto.attributes.items()
            },
            schema_id=json_value_proto.schema_id,
        )

    def to_protobuf(self) -> JsonValueProto:
        """Convert this JsonValue to a protobuf JsonValue message."""
        json_value_proto = JsonValueProto(schema_id=self.schema_id)
        json_format.ParseDict(dict(self.value), json_value_proto.value)
        for key, attribute in self.attributes.items():
            json_value_proto.attributes[key].CopyFrom(_attribute_to_protobuf(attribute))
        return json_value_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, JsonValue):
            return NotImplemented
        return (
            self.value == other.value
            and self.attributes == other.attributes
            and self.schema_id == other.schema_id
        )

    def __repr__(self) -> str:
        """Return a representation of the JsonValue."""
        return (
            f"JsonValue({dict(self.value)!r}, attributes={dict(self.attributes)!r}, "
            f"schema_id={self.schema_id!r})"
        )


def json_value_from_protobuf(json_value_proto: JsonValueProto) -> dict[str, Any] | JsonValue:
    """Return a plain dictionary, or a JsonValue when attributes or a schema are present."""
    if json_value_proto.attributes or json_value_proto.schema_id:
        return JsonValue.from_protobuf(json_value_proto)
    return json_format.MessageToDict(json_value_proto.value)


def _attribute_to_protobuf(value: AttributeValueType) -> AttributeValue:
    if isinstance(value, bool):
        return AttributeValue(bool_value=value)
    if isinstance(value, int):
        return AttributeValue(integer_value=value)
    if isinstance(value, float):
        return AttributeValue(double_value=value)
    if isinstance(value, str):
        return AttributeValue(string_value=value)
    raise TypeError(f"JsonValue attributes must be bool, int, float, or str, not {type(value)}.")
