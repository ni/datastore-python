# V2 Example Notebooks

The Jupyter Notebooks in the sub-directories of this directory demonstrate the
V2 Measurement Data Store Python API, `ni.datastore.data.v2`. They are the V2
companions of the notebooks in the parent directory.

V2 reuses the V1 Metadata API, so these notebooks create and read metadata with
`ni.datastore.metadata`, as the V1 notebooks do.

## Setup

These notebooks use the main Python environment / kernel of `ni.datastore`. To
execute the code in these notebooks, first execute the following command from
the repo's root directory:

```sh
poetry install
```

After executing this command, select the environment that it creates as the
kernel to use for executing any of the provided notebooks.

The notebooks need NI Measurement Data Services running in V2 mode. By
default, the clients use discovery to find the service. To connect to a specific
service instance, set the `MDS_V2_GRPC_TARGET` environment variable to its gRPC
target, such as `[::1]:59606`, before starting Jupyter.

## Notebooks

- `overview/publish_measurement.ipynb`: Publish a waveform measurement with a
  condition, then query and read it back.
- `query/publish_sample_data.ipynb`: Create sample data for the query notebook.
  Run this first.
- `query/query_measurements.ipynb`: Query test results, steps, measurements, and
  conditions with OData.
- `publish/batch_create.ipynb`: Create test results, steps, and measurements in
  atomic batches, including nested steps and measurements.
- `measurement-values/measurement_values.ipynb`: Scalar and non-scalar
  measurement values, and limits.
- `update-delete/update_delete.ipynb`: Update fields, change conditions, link
  metadata, and delete data.
- `structured-extensions/structured_extensions.ipynb`: Store nested JSON data in
  extensions.
