"""
Example usage of the uchygiene library.

Prerequisites:
    - Databricks CLI configured with a profile, or
    - Environment variables DATABRICKS_HOST and DATABRICKS_TOKEN set

Run this script from the project root:
    python examples/basic_usage.py
"""

from uchygiene import (
    UCHygieneClient,
    check_catalog_comments,
    check_schema_comments,
    check_table_comments,
    check_column_comments,
    check_table_owners,
    ConsoleReporter,
    JsonReporter,
)
from uchygiene.checks import run_all_checks


def main():
    # Initialise the client
    # Uses default authentication (env vars or Databricks CLI profile)
    client = UCHygieneClient()
    
    # Or specify a profile explicitly:
    # client = UCHygieneClient(profile="my-workspace")
    
    print("Connected to Databricks workspace")
    print("Running hygiene checks...\n")
    
    # Option 1: Run all checks at once
    results = run_all_checks(client)
    
    # Option 2: Run specific checks
    # results = []
    # results.extend(check_catalog_comments(client))
    # results.extend(check_table_comments(client, catalog_filter="my_catalog"))
    
    # Option 3: Limit scope to a specific catalog/schema
    # results = run_all_checks(
    #     client,
    #     catalog_filter="production",
    #     schema_filter="sales",
    # )
    
    # Output results to console
    reporter = ConsoleReporter()
    reporter.report(results)
    
    # Or get JSON output
    # json_reporter = JsonReporter()
    # print(json_reporter.report(results))


if __name__ == "__main__":
    main()
