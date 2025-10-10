########
Examples
########

This section contains Jupyter notebook examples demonstrating how to use the NI Data Store.

All example notebooks are located in the ``examples/notebooks/`` directory of the repository.

OData Query Examples
====================

These notebooks demonstrate how to query data and metadata using OData syntax:

**Setup and Sample Data:**

* `publish_sample_data.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/query/publish_sample_data.ipynb>`_ - Creates comprehensive sample data for query examples

**Query Examples:**

* `query_metadata.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/query/query_metadata.ipynb>`_ - Demonstrates metadata queries (operators, hardware, UUTs, etc.)
* `query_measurements.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/query/query_measurements.ipynb>`_ - Demonstrates measurement and condition queries

Other Examples
==============

Additional examples for various use cases:

* `publish_measurement.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/overview/publish_measurement.ipynb>`_ - Basic measurement publishing
* `alias.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/alias/alias.ipynb>`_ - Working with aliases
* `custom_metadata.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/custom-metadata/custom_metadata.ipynb>`_ - Custom metadata examples
* `publish_waveforms.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/voltage-regulator/publish_waveforms.ipynb>`_ - Publishing waveform data

Getting Started
===============

1. **Run the setup notebook first:** Start with ``publish_sample_data.ipynb`` to create sample data
2. **Explore queries:** Try the OData query examples to learn filtering and data retrieval
3. **Adapt for your use case:** Use the other examples as templates for your specific needs

All notebooks include detailed explanations and can be run in any Jupyter environment with the ``ni.datastore`` package installed.