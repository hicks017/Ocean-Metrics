import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.storage import load_ddl

class TestLoadDDL(unittest.TestCase):

    @patch("src.storage.ROOT", Path("/mock/root"))
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.read_text", return_value="CREATE TABLE mock_table (id INTEGER PRIMARY KEY);")
    def test_load_ddl_success(self, mock_read_text, mock_exists):
        table_name = "mock_table"
        ddl = load_ddl(table_name)

        # Assert the correct file path was checked
        mock_exists.assert_called_once_with()
        # Assert the file content was read
        mock_read_text.assert_called_once_with()
        # Assert the returned DDL matches the mock content
        self.assertEqual(ddl, "CREATE TABLE mock_table (id INTEGER PRIMARY KEY);")

    @patch("src.storage.ROOT", Path("/mock/root"))
    @patch("pathlib.Path.exists", return_value=False)
    def test_load_ddl_missing_file(self, mock_exists):
        table_name = "nonexistent_table"

        with self.assertRaises(FileNotFoundError) as context:
            load_ddl(table_name)

        # Assert the correct file path was checked
        mock_exists.assert_called_once_with()
        # Assert the exception message matches
        self.assertEqual(str(context.exception), "DDL not found: /mock/root/sql/init_table_nonexistent_table.sql")

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
