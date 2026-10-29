# Overview V2 Example

`overview-v2` contains sample Python code for writing to and reading from
the NI Measurement Data Store when the service runs in V2 mode.

It is the V2 companion of the [`overview`](../overview/) example. Data is
published with `ni.datastore.data.v2`, and metadata is created with
`ni.datastore.metadata`, because V2 reuses the V1 Metadata API.

## Required Software

`overview-v2` requires Python 3.10 or greater, and a Measurement Data
Services instance started in V2 mode.

## Usage

```python
poetry install
poetry run overview-v2
```

By default, the clients use discovery to find the service. To connect to a
specific service instance, pass its gRPC target:

```python
poetry run overview-v2 --grpc-target "[::1]:59606"
```
