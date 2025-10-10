import unittest
from unittest.mock import MagicMock, patch, call
from src.storage import init_db

class TestInitDB(unittest.TestCase):

    @patch("src.storage.load_ddl")
    def test_creates_tables_and_indexes(self, mock_load_ddl):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"

        init_db(mock_conn)

        # Assert tables are created with correct id_def
        id_def = "SERIAL PRIMARY KEY"
        for table in ["wind", "swell", "temps", "energy"]:
            mock_cursor.execute.assert_any_call(f"CREATE TABLE {table} (id {id_def});")

        # Assert indexes are created with correct SQL
        for table in ["wind", "swell", "temps", "energy"]:
            for col in ["Date_utc", "station"]:
                idx = f"idx_{table}_{col.lower()}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col});"
                mock_cursor.execute.assert_any_call(sql)

        # Assert commit is called once
        mock_conn.commit.assert_called_once()

    @patch("src.storage.load_ddl", side_effect=FileNotFoundError("DDL not found"))
    def test_ddl_load_failure(self, mock_load_ddl):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value

        init_db(mock_conn)

        # Assert no table creation SQL is executed
        mock_cursor.execute.assert_not_called()
        # Assert commit is still called once
        mock_conn.commit.assert_called_once()

    @patch("src.storage.load_ddl")
    def test_create_table_failure(self, mock_load_ddl):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"
        mock_cursor.execute.side_effect = [
            Exception("CREATE TABLE failed"),  # Fail on first table creation
            None, None, None, None, None, None, None  # Remaining calls succeed
        ]

        init_db(mock_conn)

        # Assert commit is called once
        mock_conn.commit.assert_called_once()

    @patch("src.storage.load_ddl")
    def test_create_index_failure(self, mock_load_ddl):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"
        mock_cursor.execute.side_effect = [
            None,  # CREATE TABLE succeeds
            Exception("CREATE INDEX failed"),  # Fail on first index creation
            None, None, None, None, None, None  # Remaining calls succeed
        ]

        init_db(mock_conn)

        # Assert commit is called once
        mock_conn.commit.assert_called_once()

    @patch("src.storage.load_ddl")
    def test_create_table_before_index(self, mock_load_ddl):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"

        init_db(mock_conn)

        # Assert CREATE TABLE appears before CREATE INDEX for each table
        for table in ["wind", "swell", "temps", "energy"]:
            create_table_call = call(f"CREATE TABLE {table} (id SERIAL PRIMARY KEY);")
            create_index_calls = [
                call(f"CREATE INDEX IF NOT EXISTS idx_{table}_date_utc ON {table}(Date_utc);"),
                call(f"CREATE INDEX IF NOT EXISTS idx_{table}_station ON {table}(station);")
            ]
            self.assertLess(
                mock_cursor.execute.mock_calls.index(create_table_call),
                min(mock_cursor.execute.mock_calls.index(c) for c in create_index_calls)
            )

if __name__ == "__main__":
    unittest.main()