# Pytest Testing Example

This example demonstrates using the `ni.datastore.testing` pytest fixtures and decorators to automatically publish test results and measurements to the NI Data Store.

## Overview

This example shows how to:
- Use the `@publish_test_to_datastore` decorator to automatically create test steps
- Use the `log` fixture to publish measurements and perform checks
- Automatically extract variable names for measurement naming
- Use parameterized tests with datastore integration
- Register custom schemas for metadata validation

## Setup

This example uses [uv](https://github.com/astral-sh/uv) for dependency management. If you don't have uv installed, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install dependencies:

```bash
cd examples/pytest-testing
uv sync --prerelease=allow
```

## Configuration

Edit `.env` in this directory to configure the Data Store service connection:

```bash
DATASTORE_HOST=localhost
DATASTORE_PORT=50051
```

## Running Tests

Run all tests:

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

Run a specific test file:

```bash
uv run pytest tests/test_pmic.py
```

## Example Structure

- `tests/test_pmic.py` - Example PMIC (Power Management IC) tests demonstrating:
  - Parameterized tests with multiple voltage setpoints and current limits
  - Using `log.record()` to publish measurements with automatic variable name extraction
  - Using `log.check_lt()`, `log.check_gt()`, `log.check_eq()` for assertion-based measurements
  - Custom test fixtures for simulating hardware measurements

- `tests/test_pmic.schema.toml` - Custom schema defining metadata validation rules for:
  - Hardware items (PMIC devices)
  - Operators (test engineers)
  - Test adapters (test fixtures and boards)

- `tests/conftest.py` - Pytest configuration including:
  - Loading environment variables from `.env`
  - Importing datastore testing fixtures
  - Custom fixtures for PMIC measurement simulation

## Key Features Demonstrated

### Automatic Test Step Creation

The `@publish_test_to_datastore` decorator automatically creates a step in the data store for each test function, including parameterized tests.

### Measurement Publishing

Three methods for publishing measurements:

1. **`log.record(value, name=None)`** - Publish a measurement with automatic variable name extraction
2. **`log.check_gt(value, expected, name=None)`** - Check value > expected, publish with outcome
3. **`log.check_lt(value, expected, name=None)`** - Check value < expected, publish with outcome
4. **`log.check_eq(value, expected, epsilon, name=None)`** - Check equality within tolerance, publish with outcome

### Schema Registration

Custom schemas are automatically registered when placed in the `tests/` directory with the naming pattern:
- `test_*.schema.toml` or `test_*.schema.json`
- `*_test.schema.toml` or `*_test.schema.json`

## Example Output

When tests run, they automatically:
1. Create a test result in the data store
2. Register custom schemas (if present)
3. Create metadata (operators, test stations, etc.)
4. Create test steps for each test function
5. Publish parameter values as conditions
6. Publish measurements with outcomes based on checks
7. Clean up connections on teardown

All data is accessible via the Data Store API for analysis, reporting, and traceability.
