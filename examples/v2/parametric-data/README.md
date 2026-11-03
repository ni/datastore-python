# Parametric Data Example

`parametric-data` contains sample Python code for writing to and reading from
the NI Measurement Data Store V2 APIs with parametric test data.

The example characterizes a small audio amplifier driven by a fixed 1 kHz
input signal. Each test records the amplifier's output voltage in volts under
two conditions: `ambient_temperature` in degrees Celsius and `supply_voltage`
in volts. Varying these conditions across tests makes it possible to compare
the amplifier's output across its operating range.

Measurements are published with `ni.datastore.data.v2`. Test metadata is
created with `ni.datastore.metadata`, because V2 reuses the V1 Metadata API.

## Required Software

`parametric-data` requires Python 3.11 or greater, and a Measurement Data
Services instance started in V2 mode.

## Usage

```python
poetry install
poetry run parametric-data
```

By default, the clients use discovery to find the service. To connect to a
specific service instance, pass its gRPC target:

```python
poetry run parametric-data --grpc-target "[::1]:59606"
```
