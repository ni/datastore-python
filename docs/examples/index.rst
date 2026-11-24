####################
Runnable V2 examples
####################

These Jupyter notebooks demonstrate the V2 Data Store API with complete,
executable workflows. They are supporting examples rather than prerequisites
for the tutorial. See the
`V2 notebook setup guide <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/README.md>`_
for dependencies and service connection details.

The notebooks use a dedicated Poetry environment. From the repository root:

.. code-block:: powershell

   cd examples\notebooks
   poetry install

Select that environment as the notebook kernel. The notebooks require NI
Measurement Data Services running in V2 mode.

Publishing and reading
======================

* `Publish and read a measurement <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/overview/publish_measurement.ipynb>`_
  creates a waveform measurement with a condition, then queries and reads it.
* `Measurement value types <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/measurement-values/measurement_values.ipynb>`_
  demonstrates scalar and non-scalar values and limits.
* `Batch creation <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/batch-create/batch_create.ipynb>`_
  creates test results, steps, and measurements in atomic batches.

Querying and managing data
==========================

* `Publish query sample data <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/query/publish_sample_data.ipynb>`_
  creates data for the query notebook. Run it first.
* `Query V2 data <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/query/query_data.ipynb>`_
  queries test results, steps, measurements, and conditions with OData.
* `Update and delete resources <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/update-delete/update_delete.ipynb>`_
  updates fields, changes conditions, links metadata, and deletes data.
* `Structured extensions <https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/structured-extensions/structured_extensions.ipynb>`_
  stores nested JSON data in extensions.
