"""
uchygiene - Unity Catalog hygiene checker for Databricks.
"""

__version__ = "0.1.0"

from .client import UCHygieneClient
from .checks import (
    CheckResult,
    CheckSeverity,
    check_table_comments,
    check_column_comments,
    check_table_owners,
    check_schema_comments,
    check_catalog_comments,
)
from .reporters import ConsoleReporter, JsonReporter

__all__ = [
    "UCHygieneClient",
    "CheckResult",
    "CheckSeverity",
    "check_table_comments",
    "check_column_comments",
    "check_table_owners",
    "check_schema_comments",
    "check_catalog_comments",
    "ConsoleReporter",
    "JsonReporter",
]
