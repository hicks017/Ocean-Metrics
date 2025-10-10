import unittest
from unittest.mock import patch, MagicMock
from src.storage import get_connection

class TestGetConnection(unittest.TestCase):

    @patch("src.storage.psycopg.connect")
    @patch("src.storage.USE_POSTGRES", True)
    @patch("src.storage.POSTGRES_VARS", {"dbname": "testdb", "user": "testuser", "password": "testpass"})
    def test_postgres_connection(self, mock_connect):
        # Mock the connection object returned by psycopg
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_connection()

        # Assert psycopg.connect was called with POSTGRES_VARS
        mock_connect.assert_called_once_with(dbname="testdb", user="testuser", password="testpass")
        # Assert the returned connection is the mocked connection
        self.assertEqual(conn, mock_conn)

    @patch("src.storage.sqlite3.connect")
    @patch("src.storage.USE_POSTGRES", False)
    @patch("src.storage.SQLITE_FILE", "test.db")
    def test_sqlite_connection(self, mock_connect):
        # Mock the connection object returned by sqlite3
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_connection()

        # Assert sqlite3.connect was called with SQLITE_FILE
        mock_connect.assert_called_once_with("test.db")
        # Assert the returned connection is the mocked connection
        self.assertEqual(conn, mock_conn)

    @patch("src.storage.psycopg.connect", side_effect=Exception("Postgres connection failed"))
    @patch("src.storage.USE_POSTGRES", True)
    @patch("src.storage.POSTGRES_VARS", {"dbname": "testdb", "user": "testuser", "password": "testpass"})
    def test_postgres_connection_failure(self, mock_connect):
        with self.assertRaises(Exception) as context:
            get_connection()

        # Assert the exception message matches
        self.assertEqual(str(context.exception), "Postgres connection failed")

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
