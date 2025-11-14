"""UUT data type for the Data Store Client."""

from __future__ import annotations

from typing import Iterable, Mapping, MutableMapping, MutableSequence

from ni.datastore.metadata._grpc_conversion import (
    populate_extension_value_message_map,
    populate_from_extension_value_message_map,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import (
    Uut as UutProto,
)


class Uut:
    """Represents the metadata of a Unit Under Test (UUT).

    A UUT represents a model or type of device that can be tested, containing
    information like model name, family, manufacturers, and part number that
    describe the UUT type rather than specific instances.


    """

    __slots__ = (
        "_id",
        "model_name",
        "family",
        "_manufacturers",
        "part_number",
        "link",
        "_extension",
        "schema_id",
    )

    @property
    def manufacturers(self) -> MutableSequence[str]:
        """The manufacturers of the UUT."""
        return self._manufacturers

    @property
    def extension(self) -> MutableMapping[str, str]:
        """The extension of the UUT."""
        return self._extension

    @property
    def id(self) -> str:
        """The string id of the uut."""
        return self._id

    def __init__(
        self,
        *,
        model_name: str = "",
        family: str = "",
        manufacturers: Iterable[str] | None = None,
        part_number: str = "",
        link: str = "",
        extension: Mapping[str, str] | None = None,
        schema_id: str = "",
    ) -> None:
        """Initialize a Uut instance.

        Args:
            model_name: The name of the UUT model.
            family: The UUT family.
            manufacturers: List of manufacturers of the UUT.
            part_number: The part number of the UUT.
            link: A link to a resource that describes the UUT. This value is
                expected to be a valid URI.
            extension: Any extensions to be associated with the UUT.
            schema_id: The unique identifier of the schema that applies to this
                instance's extension. If any extension is associated with this
                instance, a schema_id must be provided, unless the UUT is
                created within the context of a test result, in which case the
                test result must have a schema_id.
        """
        self._id = ""
        self.model_name = model_name
        self.family = family
        self._manufacturers: MutableSequence[str] = (
            list(manufacturers) if manufacturers is not None else []
        )
        self.part_number = part_number
        self.link = link
        self._extension: MutableMapping[str, str] = dict(extension) if extension is not None else {}
        self.schema_id = schema_id

    @staticmethod
    def from_protobuf(uut_proto: UutProto) -> "Uut":
        """Create a Uut instance from a protobuf Uut message."""
        uut = Uut(
            model_name=uut_proto.model_name,
            family=uut_proto.family,
            manufacturers=uut_proto.manufacturers,
            part_number=uut_proto.part_number,
            link=uut_proto.link,
            schema_id=uut_proto.schema_id,
        )
        populate_from_extension_value_message_map(uut.extension, uut_proto.extension)
        uut._id = uut_proto.id
        return uut

    def to_protobuf(self) -> UutProto:
        """Convert this Uut to a protobuf Uut message."""
        uut_proto = UutProto(
            id=self.id,
            model_name=self.model_name,
            family=self.family,
            manufacturers=self.manufacturers,
            part_number=self.part_number,
            link=self.link,
            schema_id=self.schema_id,
        )
        populate_extension_value_message_map(uut_proto.extension, self.extension)
        return uut_proto

    def __eq__(self, other: object) -> bool:
        """Determine equality."""
        if not isinstance(other, Uut):
            return NotImplemented
        return (
            self.id == other.id
            and self.model_name == other.model_name
            and self.family == other.family
            and self.manufacturers == other.manufacturers
            and self.part_number == other.part_number
            and self.link == other.link
            and self.extension == other.extension
            and self.schema_id == other.schema_id
        )

    def __str__(self) -> str:
        """Return a string representation of the Uut."""
        return str(self.to_protobuf())
