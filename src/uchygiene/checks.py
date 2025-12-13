"""
Hygiene check functions for Unity Catalog objects.

Each check function examines a specific aspect of catalog hygiene
and returns a list of CheckResult objects describing any issues found.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .client import UCHygieneClient


class CheckSeverity(Enum):
    """Severity level for hygiene check results."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CheckResult:
    """Represents the result of a single hygiene check."""
    
    check_name: str
    severity: CheckSeverity
    object_type: str
    object_name: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


def check_catalog_comments(client: UCHygieneClient) -> list[CheckResult]:
    """
    Check that all catalogs have comments/descriptions.

    Args:
        client: The UCHygieneClient instance.

    Returns:
        List of CheckResult for catalogs missing comments.
    """
    results = []
    
    for catalog in client.list_catalogs():
        if not catalog.comment:
            results.append(
                CheckResult(
                    check_name="catalog_comment",
                    severity=CheckSeverity.WARNING,
                    object_type="catalog",
                    object_name=catalog.name,
                    message=f"Catalog '{catalog.name}' has no description",
                )
            )
    
    return results


def check_schema_comments(
    client: UCHygieneClient,
    catalog_filter: str | None = None,
) -> list[CheckResult]:
    """
    Check that all schemas have comments/descriptions.

    Args:
        client: The UCHygieneClient instance.
        catalog_filter: Optional catalog name to limit scope.

    Returns:
        List of CheckResult for schemas missing comments.
    """
    results = []
    
    catalogs = client.list_catalogs()
    
    for catalog in catalogs:
        if catalog_filter and catalog.name != catalog_filter:
            continue
            
        try:
            schemas = client.list_schemas(catalog.name)
        except Exception:
            continue
            
        for schema in schemas:
            if not schema.comment:
                results.append(
                    CheckResult(
                        check_name="schema_comment",
                        severity=CheckSeverity.WARNING,
                        object_type="schema",
                        object_name=f"{catalog.name}.{schema.name}",
                        message=f"Schema '{catalog.name}.{schema.name}' has no description",
                    )
                )
    
    return results


def check_table_comments(
    client: UCHygieneClient,
    catalog_filter: str | None = None,
    schema_filter: str | None = None,
) -> list[CheckResult]:
    """
    Check that all tables have comments/descriptions.

    Args:
        client: The UCHygieneClient instance.
        catalog_filter: Optional catalog name to limit scope.
        schema_filter: Optional schema name to limit scope.

    Returns:
        List of CheckResult for tables missing comments.
    """
    results = []
    
    for catalog_name, schema_name, table in client.iter_all_tables(
        catalog_filter=catalog_filter,
        schema_filter=schema_filter,
    ):
        if not table.comment:
            full_name = f"{catalog_name}.{schema_name}.{table.name}"
            results.append(
                CheckResult(
                    check_name="table_comment",
                    severity=CheckSeverity.WARNING,
                    object_type="table",
                    object_name=full_name,
                    message=f"Table '{full_name}' has no description",
                )
            )
    
    return results


def check_column_comments(
    client: UCHygieneClient,
    catalog_filter: str | None = None,
    schema_filter: str | None = None,
) -> list[CheckResult]:
    """
    Check that all columns have comments/descriptions.

    Args:
        client: The UCHygieneClient instance.
        catalog_filter: Optional catalog name to limit scope.
        schema_filter: Optional schema name to limit scope.

    Returns:
        List of CheckResult for columns missing comments.
    """
    results = []
    
    for catalog_name, schema_name, table in client.iter_all_tables(
        catalog_filter=catalog_filter,
        schema_filter=schema_filter,
    ):
        full_name = f"{catalog_name}.{schema_name}.{table.name}"
        
        try:
            columns = client.get_table_columns(full_name)
        except Exception:
            continue
            
        columns_without_comments = [
            col.name for col in columns 
            if not col.comment
        ]
        
        if columns_without_comments:
            results.append(
                CheckResult(
                    check_name="column_comment",
                    severity=CheckSeverity.INFO,
                    object_type="table",
                    object_name=full_name,
                    message=f"Table '{full_name}' has {len(columns_without_comments)} columns without descriptions",
                    details={"columns": columns_without_comments},
                )
            )
    
    return results


def check_table_owners(
    client: UCHygieneClient,
    catalog_filter: str | None = None,
    schema_filter: str | None = None,
) -> list[CheckResult]:
    """
    Check that all tables have an owner assigned.

    Args:
        client: The UCHygieneClient instance.
        catalog_filter: Optional catalog name to limit scope.
        schema_filter: Optional schema name to limit scope.

    Returns:
        List of CheckResult for tables without owners.
    """
    results = []
    
    for catalog_name, schema_name, table in client.iter_all_tables(
        catalog_filter=catalog_filter,
        schema_filter=schema_filter,
    ):
        if not table.owner:
            full_name = f"{catalog_name}.{schema_name}.{table.name}"
            results.append(
                CheckResult(
                    check_name="table_owner",
                    severity=CheckSeverity.WARNING,
                    object_type="table",
                    object_name=full_name,
                    message=f"Table '{full_name}' has no owner assigned",
                )
            )
    
    return results


def check_empty_schemas(
    client: UCHygieneClient,
    catalog_filter: str | None = None,
) -> list[CheckResult]:
    """
    Check for schemas that contain no tables.

    Args:
        client: The UCHygieneClient instance.
        catalog_filter: Optional catalog name to limit scope.

    Returns:
        List of CheckResult for empty schemas.
    """
    results = []
    
    catalogs = client.list_catalogs()
    
    for catalog in catalogs:
        if catalog_filter and catalog.name != catalog_filter:
            continue
            
        try:
            schemas = client.list_schemas(catalog.name)
        except Exception:
            continue
            
        for schema in schemas:
            # Skip information_schema and other system schemas
            if schema.name.startswith("information_schema"):
                continue
                
            try:
                tables = client.list_tables(catalog.name, schema.name)
                if len(list(tables)) == 0:
                    results.append(
                        CheckResult(
                            check_name="empty_schema",
                            severity=CheckSeverity.INFO,
                            object_type="schema",
                            object_name=f"{catalog.name}.{schema.name}",
                            message=f"Schema '{catalog.name}.{schema.name}' contains no tables",
                        )
                    )
            except Exception:
                continue
    
    return results


def run_all_checks(
    client: UCHygieneClient,
    catalog_filter: str | None = None,
    schema_filter: str | None = None,
) -> list[CheckResult]:
    """
    Run all hygiene checks and return combined results.

    Args:
        client: The UCHygieneClient instance.
        catalog_filter: Optional catalog name to limit scope.
        schema_filter: Optional schema name to limit scope.

    Returns:
        Combined list of all CheckResult objects.
    """
    results = []
    
    results.extend(check_catalog_comments(client))
    results.extend(check_schema_comments(client, catalog_filter))
    results.extend(check_table_comments(client, catalog_filter, schema_filter))
    results.extend(check_column_comments(client, catalog_filter, schema_filter))
    results.extend(check_table_owners(client, catalog_filter, schema_filter))
    results.extend(check_empty_schemas(client, catalog_filter))
    
    return results
