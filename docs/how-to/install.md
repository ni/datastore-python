# Install and connect to MDS V2

Use this guide to prepare a Python environment for the V2 Data Store client
and connect it to NI Measurement Data Services.

## Requirements

- CPython 3.11 or later
- NI Measurement Data Services Software 2026 Q4 or later
- A Data Store service configured to run in V2 mode

Install the NI Measurement Data Services software on the target machine using
NI Package Manager. The Python package is a client; it does not install or run
the service.

## Install the Python package

Create and activate a virtual environment, then install the package:

.. code-block:: powershell

   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install ni.datastore

On Linux, use the system's Python 3.11 executable and activate the environment
with its `bin/activate` script.

Verify that the V2 client can be imported:

.. code-block:: console

   python -c "from ni.datastore.data.v2 import DataStoreClient; print(DataStoreClient.__name__)"

## Connect to a V2 Data Store service

By default, `DataStoreClient` uses MeasurementLink discovery to locate a V2
Data Store service:

```python
from ni.datastore.data.v2 import DataStoreClient

with DataStoreClient() as client:
    test_result = client.create_test_result("Connection check")
```

If your application must connect to a specific service, pass a gRPC channel
using the `grpc_channel` argument. See the [client reference](../reference/ni-data-store-v2.md)
for details. The V2 notebooks also document how to configure a target for
their own setup.

## Run the examples

The repository's Jupyter notebooks use a separate Poetry environment. Follow
the setup instructions in the [V2 notebook guide](https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/README.md).
