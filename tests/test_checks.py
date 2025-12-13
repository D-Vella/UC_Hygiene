"""Tests for the hygiene checks module using mocked Databricks SDK."""

import pytest
from unittest.mock import Mock, MagicMock

from uchygiene.client import UCHygieneClient
from uchygiene.checks import (
    CheckSeverity,
    check_catalog_comments,
    check_schema_comments,
    check_table_comments,
    check_column_comments,
    check_table_owners,
    check_empty_schemas,
)


@pytest.fixture
def mock_client():
    """Create a UCHygieneClient with a mocked WorkspaceClient."""
    client = UCHygieneClient.__new__(UCHygieneClient)
    client._workspace = MagicMock()
    return client


class TestCheckCatalogComments:
    """Tests for catalog comment checks."""

    def test_no_issues_when_all_have_comments(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        mock_catalog.comment = "This is a well-documented catalog"
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        
        results = check_catalog_comments(mock_client)
        
        assert len(results) == 0

    def test_flags_catalog_without_comment(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "undocumented_catalog"
        mock_catalog.comment = None
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        
        results = check_catalog_comments(mock_client)
        
        assert len(results) == 1
        assert results[0].check_name == "catalog_comment"
        assert results[0].severity == CheckSeverity.WARNING
        assert results[0].object_name == "undocumented_catalog"

    def test_flags_catalog_with_empty_comment(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "empty_comment_catalog"
        mock_catalog.comment = ""
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        
        results = check_catalog_comments(mock_client)
        
        assert len(results) == 1


class TestCheckSchemaComments:
    """Tests for schema comment checks."""

    def test_no_issues_when_all_have_comments(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "my_schema"
        mock_schema.comment = "Well documented schema"
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        
        results = check_schema_comments(mock_client)
        
        assert len(results) == 0

    def test_flags_schema_without_comment(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "undocumented_schema"
        mock_schema.comment = None
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        
        results = check_schema_comments(mock_client)
        
        assert len(results) == 1
        assert results[0].object_name == "my_catalog.undocumented_schema"

    def test_respects_catalog_filter(self, mock_client):
        mock_catalog_1 = Mock()
        mock_catalog_1.name = "catalog_1"
        
        mock_catalog_2 = Mock()
        mock_catalog_2.name = "catalog_2"
        
        mock_schema = Mock()
        mock_schema.name = "undocumented_schema"
        mock_schema.comment = None
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog_1, mock_catalog_2]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        
        results = check_schema_comments(mock_client, catalog_filter="catalog_1")
        
        # Should only check catalog_1
        assert all("catalog_1" in r.object_name for r in results)


class TestCheckTableComments:
    """Tests for table comment checks."""

    def test_flags_table_without_comment(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "my_schema"
        
        mock_table = Mock()
        mock_table.name = "undocumented_table"
        mock_table.comment = None
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        mock_client._workspace.tables.list.return_value = [mock_table]
        
        results = check_table_comments(mock_client)
        
        assert len(results) == 1
        assert results[0].object_name == "my_catalog.my_schema.undocumented_table"


class TestCheckColumnComments:
    """Tests for column comment checks."""

    def test_flags_columns_without_comments(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "my_schema"
        
        mock_table = Mock()
        mock_table.name = "my_table"
        mock_table.comment = "Table has comment"
        
        mock_col_1 = Mock()
        mock_col_1.name = "documented_col"
        mock_col_1.comment = "This column is documented"
        
        mock_col_2 = Mock()
        mock_col_2.name = "undocumented_col"
        mock_col_2.comment = None
        
        mock_table_detail = Mock()
        mock_table_detail.columns = [mock_col_1, mock_col_2]
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        mock_client._workspace.tables.list.return_value = [mock_table]
        mock_client._workspace.tables.get.return_value = mock_table_detail
        
        results = check_column_comments(mock_client)
        
        assert len(results) == 1
        assert results[0].check_name == "column_comment"
        assert "undocumented_col" in results[0].details["columns"]
        assert "documented_col" not in results[0].details["columns"]


class TestCheckTableOwners:
    """Tests for table owner checks."""

    def test_no_issues_when_owner_assigned(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "my_schema"
        
        mock_table = Mock()
        mock_table.name = "my_table"
        mock_table.owner = "data_team@company.com"
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        mock_client._workspace.tables.list.return_value = [mock_table]
        
        results = check_table_owners(mock_client)
        
        assert len(results) == 0

    def test_flags_table_without_owner(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "my_schema"
        
        mock_table = Mock()
        mock_table.name = "orphan_table"
        mock_table.owner = None
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        mock_client._workspace.tables.list.return_value = [mock_table]
        
        results = check_table_owners(mock_client)
        
        assert len(results) == 1
        assert results[0].check_name == "table_owner"


class TestCheckEmptySchemas:
    """Tests for empty schema checks."""

    def test_flags_empty_schema(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "empty_schema"
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        mock_client._workspace.tables.list.return_value = []
        
        results = check_empty_schemas(mock_client)
        
        assert len(results) == 1
        assert results[0].check_name == "empty_schema"

    def test_skips_information_schema(self, mock_client):
        mock_catalog = Mock()
        mock_catalog.name = "my_catalog"
        
        mock_schema = Mock()
        mock_schema.name = "information_schema"
        
        mock_client._workspace.catalogs.list.return_value = [mock_catalog]
        mock_client._workspace.schemas.list.return_value = [mock_schema]
        mock_client._workspace.tables.list.return_value = []
        
        results = check_empty_schemas(mock_client)
        
        assert len(results) == 0
