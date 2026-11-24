# Query and read V2 data

Use the V2 Data Store query methods to find resources by their fields. Queries
use OData filter expressions. Once a Measurement is found, read its value
separately.

## Find measurements

Use a unique name or another identifying field to avoid matching unrelated
data. For example, to find measurements by a known TestResult ID:

```python
from ni.datastore.data.v2 import DataStoreClient, MeasurementField

odata_query = f"$filter=TestResultId eq {test_result_id}"

with DataStoreClient() as client:
    page = client.query_measurements(
        odata_query,
        read_fields=[MeasurementField.ID, MeasurementField.NAME],
        page_size=100,
    )
    for measurement in page:
        value = client.read_measurement_value(measurement.id)
        print(measurement.name, value)
```

`read_fields` lets a query request the resource fields it needs. Use the
`MeasurementField`, `StepField`, and `TestResultField` enums to name them.

## Read Conditions with their Step

Conditions belong to Steps. To read a Step's Conditions, request the
`CONDITIONS` field:

```python
from ni.datastore.data.v2 import DataStoreClient, StepField

with DataStoreClient() as client:
    step = client.get_step(step_id, read_fields=[StepField.CONDITIONS])
    for condition in step.conditions:
        print(condition.name, condition.value, condition.units)
```

## Follow page tokens

When results span multiple pages, pass each page's `next_page_token` to the
next query. Keep the same query and page size:

```python
with DataStoreClient() as client:
    page = client.query_measurements(odata_query, page_size=100)
    while True:
        for measurement in page:
            print(measurement.id, measurement.name)
        if not page.next_page_token:
            break
        page = client.query_measurements(
            odata_query,
            page_size=100,
            page_token=page.next_page_token,
        )
```

The [query notebook](https://github.com/ni/datastore-python/blob/main/examples/notebooks/v2/query/query_data.ipynb)
demonstrates queries across TestResults, Steps, Measurements, and Conditions.
