"""MetadataItems data type for the Data Store Client."""

from __future__ import annotations

from collections.abc import Sequence

from ni.datastore.metadata._types._hardware_item import HardwareItem
from ni.datastore.metadata._types._operator import Operator
from ni.datastore.metadata._types._software_item import SoftwareItem
from ni.datastore.metadata._types._test import Test
from ni.datastore.metadata._types._test_adapter import TestAdapter
from ni.datastore.metadata._types._test_description import TestDescription
from ni.datastore.metadata._types._test_station import TestStation
from ni.datastore.metadata._types._uut import Uut
from ni.datastore.metadata._types._uut_instance import UutInstance
from ni.measurements.metadata.v1.metadata_store_service_pb2 import (
    CreateFromJsonDocumentResponse,
)


class MetadataItems:
    """Represents a collection of metadata items created from a JSON document.

    This class contains the results of creating metadata items from a JSON document,
    organizing them by type for easy access.
    """

    __slots__ = (
        "uut_instances",
        "uuts",
        "operators",
        "test_descriptions",
        "tests",
        "test_stations",
        "hardware_items",
        "software_items",
        "test_adapters",
    )

    def __init__(
        self,
        *,
        uut_instances: Sequence[UutInstance] = (),
        uuts: Sequence[Uut] = (),
        operators: Sequence[Operator] = (),
        test_descriptions: Sequence[TestDescription] = (),
        tests: Sequence[Test] = (),
        test_stations: Sequence[TestStation] = (),
        hardware_items: Sequence[HardwareItem] = (),
        software_items: Sequence[SoftwareItem] = (),
        test_adapters: Sequence[TestAdapter] = (),
    ) -> None:
        """Initialize a MetadataItems instance.

        Args:
            uut_instances: A sequence of UUT instances created from the JSON document.
            uuts: A sequence of UUTs created from the JSON document.
            operators: A sequence of operators created from the JSON document.
            test_descriptions: A sequence of test descriptions created from the JSON document.
            tests: A sequence of tests created from the JSON document.
            test_stations: A sequence of test stations created from the JSON document.
            hardware_items: A sequence of hardware items created from the JSON document.
            software_items: A sequence of software items created from the JSON document.
            test_adapters: A sequence of test adapters created from the JSON document.
        """
        self.uut_instances = uut_instances
        self.uuts = uuts
        self.operators = operators
        self.test_descriptions = test_descriptions
        self.tests = tests
        self.test_stations = test_stations
        self.hardware_items = hardware_items
        self.software_items = software_items
        self.test_adapters = test_adapters

    @staticmethod
    def from_protobuf(response: CreateFromJsonDocumentResponse) -> "MetadataItems":
        """Create a MetadataItems instance from a protobuf CreateFromJsonDocumentResponse.

        Args:
            response: The protobuf response containing the created metadata items.

        Returns:
            MetadataItems: A new MetadataItems instance with all the created items.
        """
        return MetadataItems(
            uut_instances=[
                UutInstance.from_protobuf(uut_instance) for uut_instance in response.uut_instances
            ],
            uuts=[Uut.from_protobuf(uut) for uut in response.uuts],
            operators=[Operator.from_protobuf(operator) for operator in response.operators],
            test_descriptions=[
                TestDescription.from_protobuf(test_description)
                for test_description in response.test_descriptions
            ],
            tests=[Test.from_protobuf(test) for test in response.tests],
            test_stations=[
                TestStation.from_protobuf(test_station) for test_station in response.test_stations
            ],
            hardware_items=[
                HardwareItem.from_protobuf(hardware_item)
                for hardware_item in response.hardware_items
            ],
            software_items=[
                SoftwareItem.from_protobuf(software_item)
                for software_item in response.software_items
            ],
            test_adapters=[
                TestAdapter.from_protobuf(test_adapter) for test_adapter in response.test_adapters
            ],
        )

    def __eq__(self, other: object) -> bool:
        """Determine equality between MetadataItems instances."""
        if not isinstance(other, MetadataItems):
            return False

        return (
            list(self.uut_instances) == list(other.uut_instances)
            and list(self.uuts) == list(other.uuts)
            and list(self.operators) == list(other.operators)
            and list(self.test_descriptions) == list(other.test_descriptions)
            and list(self.tests) == list(other.tests)
            and list(self.test_stations) == list(other.test_stations)
            and list(self.hardware_items) == list(other.hardware_items)
            and list(self.software_items) == list(other.software_items)
            and list(self.test_adapters) == list(other.test_adapters)
        )

    def __str__(self) -> str:
        """Return a string representation of the MetadataItems."""
        counts = []
        if self.uut_instances:
            counts.append(f"{len(self.uut_instances)} UUT instances")
        if self.uuts:
            counts.append(f"{len(self.uuts)} UUTs")
        if self.operators:
            counts.append(f"{len(self.operators)} operators")
        if self.test_descriptions:
            counts.append(f"{len(self.test_descriptions)} test descriptions")
        if self.tests:
            counts.append(f"{len(self.tests)} tests")
        if self.test_stations:
            counts.append(f"{len(self.test_stations)} test stations")
        if self.hardware_items:
            counts.append(f"{len(self.hardware_items)} hardware items")
        if self.software_items:
            counts.append(f"{len(self.software_items)} software items")
        if self.test_adapters:
            counts.append(f"{len(self.test_adapters)} test adapters")

        if counts:
            return f"MetadataItems({', '.join(counts)})"
        else:
            return "MetadataItems(empty)"
