########
Examples
########

This section contains Jupyter notebook and Python script examples demonstrating how to use the NI Data Store.

All example notebooks are located in the ``examples/notebooks/`` directory of the repository.

Each example script has its own project folder under ``examples/``.

OData Query Example Notebooks
=============================

These notebooks demonstrate how to query data and metadata using OData syntax:

**Setup and Sample Data:**

* `publish_sample_data.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/query/publish_sample_data.ipynb>`_ - Creates comprehensive sample data for query examples

**Query Examples:**

* `query_metadata.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/query/query_metadata.ipynb>`_ - Demonstrates metadata queries (operators, hardware, UUTs, etc.)
* `query_measurements.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/query/query_measurements.ipynb>`_ - Demonstrates measurement and condition queries

Other Example Notebooks
=======================

Additional examples for various use cases:

* `publish_measurement.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/overview/publish_measurement.ipynb>`_ - Basic measurement publishing
* `alias.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/alias/alias.ipynb>`_ - Working with aliases
* `extension_attributes.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/extension-attributes/extension_attributes.ipynb>`_ - Extension attributes examples
* `publish_waveforms.ipynb <https://github.com/ni/datastore-python/blob/main/examples/notebooks/voltage-regulator/publish_waveforms.ipynb>`_ - Publishing waveform data

Getting Started with Notebooks
==============================

1. **Run the setup notebook first:** Start with ``publish_sample_data.ipynb`` to create sample data
2. **Explore queries:** Try the OData query examples to learn filtering and data retrieval
3. **Adapt for your use case:** Use the other examples as templates for your specific needs

All notebooks include detailed explanations and can be run in any Jupyter environment with the ``ni.datastore`` package installed.

Python Example Scripts
======================

These Python scripts demonstrate how to publish and query both data and metadata.

* `overview.py <https://github.com/ni/datastore-python/blob/main/examples/overview>`_ - Publishing and querying measurement data
* `system.py <https://github.com/ni/datastore-python/blob/main/examples/system>`_ - Publishing and querying system metadata

Each has a ``README.md`` file that describes its runtime requirements and usage.
