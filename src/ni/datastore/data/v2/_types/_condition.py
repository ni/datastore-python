"""Condition data type for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from google.protobuf import json_format
from ni.measurements.data.v2.data_store_pb2 import Condition as ConditionProto
from ni.protobuf.types.scalar_conversion import scalar_from_protobuf, scalar_to_protobuf
from nitypes.scalar import Scalar

from ni.datastore.data.v2._types._json_value import JsonValue, json_value_from_protobuf

_UNIT_DESCRIPTION = "NI_UnitDescription"


class Condition:
    """An operational condition, such as a temperature or supply voltage, owned by a step.

    Conditions are immutable. Adding a condition with the same name to a step
    replaces the step's association with a new condition value.
    """

    __slots__ = (
        "name",
        "value",
        "condition_type",
        "value_label",
        "units",
    )

    def __init__(
        self,
        name: str,
        value: object,
        *,
        condition_type: str = "",
        value_label: str = "",
        units: str = "",
    ) -> None:
        """Initialize a Condition instance.

        Args:
            name: The condition name, unique within a step.
            value: A bool, int, float, str, or Scalar value, a JSON mapping, or a
                JsonValue. A scalar value reads back as a plain Python value, or as
                a Scalar when it has extended properties other than units.
            condition_type (optional): The type of the condition. For example,
                "Environment" or "Setup".
            value_label (optional): A label for the value.
            units (optional): The engineering units of the value. Defaults to the
                units of a Scalar value.
        """
        self.name = name
        self.value = value
        self.condition_type = condition_type
        self.value_label = value_label
        self.units = units

    @staticmethod
    def from_protobuf(condition_proto: ConditionProto) -> "Condition":
        """Create a Condition instance from a protobuf Condition message."""
        value_kind = condition_proto.value.WhichOneof("value")
        value: object = None
        if value_kind == "scalar":
            scalar = scalar_from_protobuf(condition_proto.value.scalar)
            # Keep the Scalar only when it carries properties a plain value cannot.
            has_extra_properties = any(
                key != _UNIT_DESCRIPTION for key in scalar.extended_properties
            )
            value = scalar if has_extra_properties else scalar.value
        elif value_kind == "json_value":
            value = json_value_from_protobuf(condition_proto.value.json_value)
        return Condition(
            name=condition_proto.name,
            value=value,
            condition_type=condition_proto.condition_type,
            value_label=condition_proto.value_label,
            units=condition_proto.units,
        )

    def to_protobuf(self) -> ConditionProto:
        """Convert this Condition instance to a protobuf Condition message."""
        condition_proto = ConditionProto(
            name=self.name,
            condition_type=self.condition_type,
            value_label=self.value_label,
            units=self.units,
        )
        value = self.value
        if isinstance(value, bool):
            condition_proto.value.scalar.bool_value = value
        elif isinstance(value, int):
            condition_proto.value.scalar.sint32_value = value
        elif isinstance(value, float):
            condition_proto.value.scalar.double_value = value
        elif isinstance(value, str):
            condition_proto.value.scalar.string_value = value
        elif isinstance(value, Scalar):
            condition_proto.value.scalar.CopyFrom(scalar_to_protobuf(value))
            if not self.units:
                condition_proto.units = value.units
        elif isinstance(value, JsonValue):
            condition_proto.value.json_value.CopyFrom(value.to_protobuf())
        elif isinstance(value, Mapping):
            json_format.ParseDict(
                cast(dict[str, Any], dict(value)), condition_proto.value.json_value.value
            )
        else:
            raise TypeError(
                "Condition values must be bool, int, float, str, Scalar, a JSON mapping, "
                "or a JsonValue."
            )
        return condition_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Condition):
            return NotImplemented
        return (
            self.name == other.name
            and self.value == other.value
            and self.condition_type == other.condition_type
            and self.value_label == other.value_label
            and self.units == other.units
        )

    def __str__(self) -> str:
        """Return a string representation of the Condition."""
        return str(self.to_protobuf())
