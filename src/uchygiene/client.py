"""
Client module for connecting to Databricks Unity Catalog.

Provides a wrapper around the Databricks SDK with convenience methods
for retrieving catalog metadata.
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import (
    CatalogInfo,
    SchemaInfo,
    TableInfo,
    ColumnInfo,
)


class UCHygieneClient:
    """
    Client for interacting with Unity Catalog.
    
    Wraps the Databricks SDK and provides methods for retrieving
    catalog, schema, and table metadata for hygiene checks.
    
    Authentication is handled automatically by the Databricks SDK,
    which will use (in order of precedence):
    1. Environment variables (DATABRICKS_HOST, DATABRICKS_TOKEN)
    2. Databricks CLI profile (~/.databrickscfg)
    3. Azure CLI authentication (if on Azure)
    
    Example:
        client = UCHygieneClient()
        catalogs = client.list_catalogs()
        
        # Or with explicit profile
        client = UCHygieneClient(profile="my-workspace")
    """

    def __init__(self, profile: str | None = None):
        """
        Initialise the client.

        Args:
            profile: Optional Databricks CLI profile name to use for authentication.
                    If not provided, uses default authentication chain.
        """
        if profile:
            self._workspace = WorkspaceClient(profile=profile)
        else:
            self._workspace = WorkspaceClient()

    @property
    def workspace(self) -> WorkspaceClient:
        """Access the underlying WorkspaceClient if needed."""
        return self._workspace

    def list_catalogs(self) -> list[CatalogInfo]:
        """
        List all catalogs the user has access to.

        Returns:
            List of CatalogInfo objects.
        """
        return list(self._workspace.catalogs.list())

    def list_schemas(self, catalog_name: str) -> list[SchemaInfo]:
        """
        List all schemas in a catalog.

        Args:
            catalog_name: The name of the catalog.

        Returns:
            List of SchemaInfo objects.
        """
        return list(self._workspace.schemas.list(catalog_name=catalog_name))

    def list_tables(self, catalog_name: str, schema_name: str) -> list[TableInfo]:
        """
        List all tables in a schema.

        Args:
            catalog_name: The name of the catalog.
            schema_name: The name of the schema.

        Returns:
            List of TableInfo objects.
        """
        return list(
            self._workspace.tables.list(
                catalog_name=catalog_name, 
                schema_name=schema_name
            )
        )

    def get_table(self, full_name: str) -> TableInfo:
        """
        Get detailed information about a specific table.

        Args:
            full_name: The full three-part name (catalog.schema.table).

        Returns:
            TableInfo object with full details including columns.
        """
        return self._workspace.tables.get(full_name=full_name)

    def get_table_columns(self, full_name: str) -> list[ColumnInfo]:
        """
        Get column information for a table.

        Args:
            full_name: The full three-part name (catalog.schema.table).

        Returns:
            List of ColumnInfo objects.
        """
        table = self.get_table(full_name)
        return table.columns or []

    def iter_all_tables(
        self, 
        catalog_filter: str | None = None,
        schema_filter: str | None = None,
    ):
        """
        Iterate over all tables across catalogs and schemas.

        Args:
            catalog_filter: Optional catalog name to limit scope.
            schema_filter: Optional schema name to limit scope (requires catalog_filter).

        Yields:
            Tuples of (catalog_name, schema_name, TableInfo).
        """
        catalogs = self.list_catalogs()
        
        for catalog in catalogs:
            if catalog_filter and catalog.name != catalog_filter:
                continue
                
            try:
                schemas = self.list_schemas(catalog.name)
            except Exception:
                # Skip catalogs we can't access
                continue
                
            for schema in schemas:
                if schema_filter and schema.name != schema_filter:
                    continue
                    
                try:
                    tables = self.list_tables(catalog.name, schema.name)
                except Exception:
                    # Skip schemas we can't access
                    continue
                    
                for table in tables:
                    yield catalog.name, schema.name, table
