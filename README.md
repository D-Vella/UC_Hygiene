# Unity Catalog Hygiene Checker

A tool for checking Unity Catalog hygiene and maintenance issues in Databricks.

## Features

- **Documentation Checks**: Identify catalogs, schemas, tables, and columns missing descriptions
- **Ownership Checks**: Find tables without assigned owners
- **Structure Checks**: Detect empty schemas
- **Flexible Scope**: Run checks across entire workspace or filter to specific catalogs/schemas
- **Multiple Output Formats**: Console output with severity indicators or JSON for automation

## Installation

Clone the repository and install in development mode:

```bash
git clone https://github.com/D-Vella/UC_Hygine.git
cd UC_Hygine
python -m venv .venv
source .venv/Scripts/activate  # On Windows with Git Bash
pip install -e ".[dev]"
```

## Authentication

The tool uses the Databricks SDK which supports multiple authentication methods:

1. **Environment variables** (recommended for automation):
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-personal-access-token"
   ```

2. **Databricks CLI profile**:
   ```bash
   databricks configure --profile my-workspace
   ```
   Then use `UCHygieneClient(profile="my-workspace")`

3. **Azure CLI** (if using Azure Databricks): Automatically uses your Azure credentials

## Quick Start

```python
from uchygiene import UCHygieneClient, ConsoleReporter
from uchygiene.checks import run_all_checks

# Connect to your workspace
client = UCHygieneClient()

# Run all hygiene checks
results = run_all_checks(client)

# Display results
reporter = ConsoleReporter()
reporter.report(results)
```

## Available Checks

| Check | Description | Severity |
|-------|-------------|----------|
| `check_catalog_comments` | Catalogs without descriptions | Warning |
| `check_schema_comments` | Schemas without descriptions | Warning |
| `check_table_comments` | Tables without descriptions | Warning |
| `check_column_comments` | Tables with undocumented columns | Info |
| `check_table_owners` | Tables without assigned owners | Warning |
| `check_empty_schemas` | Schemas containing no tables | Info |

## Filtering Scope

Limit checks to specific catalogs or schemas:

```python
# Check only the 'production' catalog
results = run_all_checks(client, catalog_filter="production")

# Check only a specific schema
results = run_all_checks(
    client,
    catalog_filter="production",
    schema_filter="sales"
)
```

## Running Individual Checks

```python
from uchygiene import UCHygieneClient
from uchygiene.checks import check_table_owners, check_column_comments

client = UCHygieneClient()

# Just check table ownership
owner_issues = check_table_owners(client, catalog_filter="production")

# Just check column documentation
column_issues = check_column_comments(client, catalog_filter="production")
```

## JSON Output

For automation or integration with other tools:

```python
from uchygiene import JsonReporter

reporter = JsonReporter()
json_output = reporter.report(results)
print(json_output)

# Or get as a dictionary
data = reporter.to_dict(results)
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=uchygiene
```

## Project Structure

```
UC_Hygine/
├── src/
│   └── uchygiene/
│       ├── __init__.py
│       ├── client.py       # Databricks SDK wrapper
│       ├── checks.py       # Hygiene check functions
│       └── reporters.py    # Output formatting
├── tests/
│   └── test_checks.py
├── examples/
│   └── basic_usage.py
├── pyproject.toml
└── README.md
```

## Future Enhancements

Potential checks to add:

- Table statistics freshness (ANALYZE TABLE not run recently)
- Stale tables (not queried in X days)
- Missing clustering/Z-order configuration
- Orphaned volumes
- Permission anomalies
- Lineage gaps

## License

MIT
