import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.engine import Engine
from src.storage import get_connection

class TestGetConnection(unittest.TestCase):

    @patch("src.storage.create_engine")
    @patch("src.storage.USE_POSTGRES", True)
    @patch("src.storage.POSTGRES_VARS", {
        "host": "localhost",
        "port": "5432",
        "dbname": "testdb",
        "user": "testuser",
        "password": "testpass"
    })
    def test_postgres_connection(self, mock_create_engine):
        # Mock the engine object
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        engine = get_connection()

        # Assert create_engine was called with correct URL
        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        mock_create_engine.assert_called_once()
        self.assertEqual(mock_create_engine.call_args[0][0], expected_url)
        
        # Assert engine configuration
        self.assertEqual(engine, mock_engine)

    @patch("src.storage.create_engine")
    @patch("src.storage.USE_POSTGRES", False)
    @patch("src.storage.SQLITE_FILE", "test.db")
    def test_sqlite_connection(self, mock_create_engine):
        # Mock the engine object
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        engine = get_connection()

        # Assert create_engine was called with correct URL
        expected_url = "sqlite:///test.db"
        mock_create_engine.assert_called_once()
        self.assertEqual(mock_create_engine.call_args[0][0], expected_url)
        
        # Assert engine configuration
        self.assertEqual(engine, mock_engine)

    @patch("src.storage.create_engine")
    @patch("src.storage.USE_POSTGRES", True)
    @patch("src.storage.POSTGRES_VARS", {
        "host": "localhost",
        "port": "5432",
        "dbname": "testdb",
        "user": "testuser",
        "password": "testpass"
    })
    def test_postgres_connection_failure(self, mock_create_engine):
        # Simulate connection failure
        mock_create_engine.side_effect = Exception("Database connection failed")

        with self.assertRaises(Exception) as context:
            get_connection()

        # Assert the exception message matches
        self.assertEqual(str(context.exception), "Database connection failed")

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
