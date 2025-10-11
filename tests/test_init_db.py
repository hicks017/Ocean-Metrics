import unittest
from unittest.mock import MagicMock, patch, call
from sqlalchemy.engine import Engine
from src.storage import init_db, text

class TestInitDB(unittest.TestCase):

    @patch("src.storage.load_ddl")
    @patch("src.storage.USE_POSTGRES", new_callable=lambda: True)
    def test_creates_tables_and_indexes_postgres(self, mock_use_postgres, mock_load_ddl):
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"

        init_db(mock_engine)

        # Assert tables are created with correct id_def
        id_def = "SERIAL PRIMARY KEY"
        for table in ["wind", "swell", "temps", "energy"]:
            mock_conn.execute.assert_any_call(text(f"CREATE TABLE {table} (id {id_def});"))

        # Assert indexes are created with correct SQL
        for table in ["wind", "swell", "temps", "energy"]:
            for col in ["Date_utc", "station"]:
                idx = f"idx_{table}_{col.lower()}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col});"
                mock_conn.execute.assert_any_call(text(sql))

    @patch("src.storage.load_ddl")
    @patch("src.storage.USE_POSTGRES", new_callable=lambda: False)
    def test_creates_tables_and_indexes_sqlite(self, mock_use_postgres, mock_load_ddl):
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"

        init_db(mock_engine)

        # Assert tables are created with correct id_def
        id_def = "INTEGER PRIMARY KEY AUTOINCREMENT"
        for table in ["wind", "swell", "temps", "energy"]:
            mock_conn.execute.assert_any_call(text(f"CREATE TABLE {table} (id {id_def});"))

        # Assert indexes are created with correct SQL
        for table in ["wind", "swell", "temps", "energy"]:
            for col in ["Date_utc", "station"]:
                idx = f"idx_{table}_{col.lower()}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col});"
                mock_conn.execute.assert_any_call(text(sql))

    @patch("src.storage.load_ddl", side_effect=FileNotFoundError("DDL not found"))
    def test_ddl_load_failure(self, mock_load_ddl):
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn

        init_db(mock_engine)

        # Assert no SQL execution attempts were made
        mock_conn.execute.assert_not_called()

    @patch("src.storage.load_ddl")
    @patch("src.storage.USE_POSTGRES", new_callable=lambda: True)
    def test_create_table_failure_postgres(self, mock_use_postgres, mock_load_ddl):
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"
        mock_conn.execute.side_effect = [
            Exception("CREATE TABLE failed"),  # Fail on first table creation
            None, None, None, None, None, None, None  # Remaining calls succeed
        ]

        init_db(mock_engine)

    @patch("src.storage.load_ddl")
    @patch("src.storage.USE_POSTGRES", new_callable=lambda: True)
    def test_create_index_failure_postgres(self, mock_use_postgres, mock_load_ddl):
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"
        mock_conn.execute.side_effect = [
            None,  # CREATE TABLE succeeds
            Exception("CREATE INDEX failed"),  # Fail on first index creation
            None, None, None, None, None, None  # Remaining calls succeed
        ]

        init_db(mock_engine)

    @patch("src.storage.load_ddl")
    @patch("src.storage.USE_POSTGRES", new_callable=lambda: True)
    def test_create_table_before_index_postgres(self, mock_use_postgres, mock_load_ddl):
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_load_ddl.side_effect = lambda table: f"CREATE TABLE {table} (id {{id_def}});"

        init_db(mock_engine)

        # Assert CREATE TABLE appears before CREATE INDEX for each table
        for table in ["wind", "swell", "temps", "energy"]:
            create_table_call = call(text(f"CREATE TABLE {table} (id SERIAL PRIMARY KEY);"))
            create_index_calls = [
                call(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_date_utc ON {table}(Date_utc);")),
                call(text(f"CREATE INDEX IF NOT EXISTS idx_{table}_station ON {table}(station);"))
            ]
            self.assertLess(
                mock_conn.execute.mock_calls.index(create_table_call),
                min(mock_conn.execute.mock_calls.index(c) for c in create_index_calls)
            )

if __name__ == "__main__":
    unittest.main()