"""Helper methods to convert between python and protobuf types."""

from __future__ import annotations

import logging
from typing import MutableMapping

import numpy as np
from google.protobuf.any_pb2 import Any
from google.protobuf.internal.containers import MessageMap
from ni.measurements.data.v1.data_store_service_pb2 import (
    PublishConditionBatchRequest,
    PublishConditionRequest,
    PublishMeasurementBatchRequest,
    PublishMeasurementRequest,
)
from ni.measurements.metadata.v1.metadata_store_pb2 import ExtensionValue
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
from nitypes.complex import ComplexInt32DType
from nitypes.scalar import Scalar
from nitypes.vector import Vector
from nitypes.waveform import AnalogWaveform, ComplexWaveform, DigitalWaveform, Spectrum

_logger = logging.getLogger(__name__)


def populate_publish_condition_request_value(
    publish_request: PublishConditionRequest, value: object
) -> None:
    """Assign a value to the scalar member of PublishConditionRequest."""
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
            f"Unsupported condition value type: {type(value)}. Please consult the documentation."
        )


def populate_publish_condition_batch_request_values(
    publish_request: PublishConditionBatchRequest, values: object
) -> None:
    """Assign a value to the scalar_values vector member of PublishConditionBatchRequest."""
    # TODO: Determine whether we wish to support primitive types such as a list of float
    if isinstance(values, Vector):
        publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
    else:
        raise TypeError(
            f"Unsupported condition values type: {type(values)}. Please consult the documentation."
        )


def populate_publish_measurement_request_value(
    publish_request: PublishMeasurementRequest, value: object
) -> None:
    """Assign a value to the appropriate field of a PublishMeasurementRequest object."""
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
        if value.dtype == np.float64:
            publish_request.double_analog_waveform.CopyFrom(
                float64_analog_waveform_to_protobuf(value)
            )
        elif value.dtype == np.int16:
            publish_request.i16_analog_waveform.CopyFrom(int16_analog_waveform_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported AnalogWaveform dtype: {value.dtype}")
    elif isinstance(value, ComplexWaveform):
        if value.dtype == np.complex128:
            publish_request.double_complex_waveform.CopyFrom(
                float64_complex_waveform_to_protobuf(value)
            )
        elif value.dtype == ComplexInt32DType:
            publish_request.i16_complex_waveform.CopyFrom(int16_complex_waveform_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported ComplexWaveform dtype: {value.dtype}")
    elif isinstance(value, Spectrum):
        if value.dtype == np.float64:
            publish_request.double_spectrum.CopyFrom(float64_spectrum_to_protobuf(value))
        else:
            raise TypeError(f"Unsupported Spectrum dtype: {value.dtype}")
    elif isinstance(value, DigitalWaveform):
        publish_request.digital_waveform.CopyFrom(digital_waveform_to_protobuf(value))
    else:
        raise TypeError(
            f"Unsupported measurement value type: {type(value)}. Please consult the documentation."
        )
    # TODO: Implement conversion from proper XYData type


def populate_publish_measurement_batch_request_values(
    publish_request: PublishMeasurementBatchRequest, values: object
) -> None:
    """Assign a value to the appropriate field of the PublishMeasurementBatchRequest object."""
    # TODO: Determine whether we wish to support primitive types such as a list of float
    if isinstance(values, Vector):
        publish_request.scalar_values.CopyFrom(vector_to_protobuf(values))
    else:
        raise TypeError(
            f"Unsupported measurement values type: {type(values)}. Please consult the documentation."
        )


def unpack_and_convert_from_protobuf_any(read_value: Any) -> object:
    """Convert from a packed pb.Any to the appropriate python object."""
    value_type = read_value.TypeName()
    if value_type == DoubleAnalogWaveform.DESCRIPTOR.full_name:
        double_analog_waveform = DoubleAnalogWaveform()
        read_value.Unpack(double_analog_waveform)
        return float64_analog_waveform_from_protobuf(double_analog_waveform)
    elif value_type == I16AnalogWaveform.DESCRIPTOR.full_name:
        i16_analog_waveform = I16AnalogWaveform()
        read_value.Unpack(i16_analog_waveform)
        return int16_analog_waveform_from_protobuf(i16_analog_waveform)
    elif value_type == DoubleComplexWaveform.DESCRIPTOR.full_name:
        double_complex_waveform = DoubleComplexWaveform()
        read_value.Unpack(double_complex_waveform)
        return float64_complex_waveform_from_protobuf(double_complex_waveform)
    elif value_type == I16ComplexWaveform.DESCRIPTOR.full_name:
        i16_complex_waveform = I16ComplexWaveform()
        read_value.Unpack(i16_complex_waveform)
        return int16_complex_waveform_from_protobuf(i16_complex_waveform)
    elif value_type == DoubleSpectrum.DESCRIPTOR.full_name:
        spectrum = DoubleSpectrum()
        read_value.Unpack(spectrum)
        return float64_spectrum_from_protobuf(spectrum)
    elif value_type == DigitalWaveformProto.DESCRIPTOR.full_name:
        digital_waveform = DigitalWaveformProto()
        read_value.Unpack(digital_waveform)
        return digital_waveform_from_protobuf(digital_waveform)
    elif value_type == DoubleXYData.DESCRIPTOR.full_name:
        xydata = DoubleXYData()
        read_value.Unpack(xydata)
        _logger.warning(
            "DoubleXYData conversion is not yet implemented. Returning the raw protobuf object."
        )
        return xydata
    elif value_type == VectorProto.DESCRIPTOR.full_name:
        vector = VectorProto()
        read_value.Unpack(vector)
        return vector_from_protobuf(vector)
    else:
        raise TypeError(f"Unsupported data type Name: {value_type}")


def populate_extension_value_message_map(
    destination: MessageMap[str, ExtensionValue],
    source: MutableMapping[str, str],
) -> None:
    """Populate a gRPC message map of string keys to ExtensionValue.

    The input is a mapping of string keys to string values.
    """
    for key, value in source.items():
        destination[key].string_value = value


def populate_from_extension_value_message_map(
    destination: MutableMapping[str, str],
    source: MessageMap[str, ExtensionValue],
) -> None:
    """Populate a mapping of string keys to stringvalues.

    The input is a gRPC message map of string keys to ExtensionValue.
    """
    for key, extension_value in source.items():
        value_case = extension_value.WhichOneof("metadata")
        if value_case == "string_value":
            destination[key] = extension_value.string_value
        else:
            raise TypeError(f"Unsupported ExtensionValue type for key '{key}': {value_case}")
