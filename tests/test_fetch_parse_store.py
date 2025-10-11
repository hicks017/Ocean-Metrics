import os
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock
import pandas as pd

# Simple logger that records calls; tests can inspect these lists
class SimpleLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.errors = []

    def info(self, msg):
        self.infos.append(msg)

    def warning(self, msg):
        self.warnings.append(msg)

    def error(self, msg):
        self.errors.append(msg)

logger = SimpleLogger()

# Stubs that will be overridden in tests if needed
def build_url(station, table):
    return f"http://example.com/{station}/{table}"

def fetch_pre_text(url):
    return "raw text"

# get_connection implemented as a context manager returning a sqlite3.Connection.
# Tests set TEST_DB_PATH to a temp file path so the DB persists across connections.
TEST_DB_PATH = None

@contextmanager
def get_connection():
    if TEST_DB_PATH is None:
        # Fallback to ephemeral in-memory connection
        conn = sqlite3.connect(":memory:")
    else:
        conn = sqlite3.connect(TEST_DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# The function under test, copied from the user prompt but using local names above.
def fetch_parse_store(station, table, parse_function, table_name):
    """Fetch data from URL, validate it, and store it in the database."""
    try:
        url = build_url(station, table)
        logger.info(f"Fetching data for {table_name} (station {station})...")
        pre_text = fetch_pre_text(url)
        logger.info(f"Parsing data for {table_name} (station {station})...")
        df = parse_function(pre_text)

        if df.empty:
            logger.warning(f"No data to insert for {table_name} (station {station}). Parsed DataFrame is empty.")
            return

        # Validate parsed data
        required_columns = ["Date_utc", "station"]
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Validation failed: Missing required columns in parsed data for {table_name} (station {station}).")
            return

        # Check for duplicates before inserting
        with get_connection() as conn:
            try:
                existing_records = conn.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE Date_utc = ? AND station = ?",
                    (df['Date_utc'].iloc[0], station)
                ).fetchone()[0]

                if existing_records > 0:
                    logger.info(f"Skipping duplicate entry for {table_name} (station {station}).")
                    return

                logger.info(f"Storing data for {table_name} (station {station})...")
                # Pandas can write to sqlite via SQLAlchemy or sqlite3 connection; use to_sql with sqlite3 requires a SQLAlchemy engine
                # We'll implement insertion manually to avoid extra dependencies:
                cols = list(df.columns)
                placeholders = ",".join(["?"] * len(cols))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"
                rows = [tuple(row) for row in df[cols].itertuples(index=False, name=None)]
                conn.executemany(insert_sql, rows)
            except Exception as db_error:
                logger.error(f"Database error while processing {table_name} (station {station}): {db_error}")
                raise
        logger.info(f"Successfully processed {table_name} (station {station}).")
    except Exception as e:
        logger.error(f"Error processing {table_name} (station {station}): {e}")

# Unit tests
class TestFetchParseStore(unittest.TestCase):
    def setUp(self):
        # Create a temp sqlite file so multiple connections share the same DB
        self.tempfile = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.tempfile.name
        self.tempfile.close()
        global TEST_DB_PATH
        TEST_DB_PATH = self.db_path

        # Create the table used by tests
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE test_table (
                    Date_utc TEXT,
                    station TEXT,
                    value REAL
                )
                """
            )
            conn.commit()

        # Reset logger
        logger.infos.clear()
        logger.warnings.clear()
        logger.errors.clear()

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except Exception:
            pass
        global TEST_DB_PATH
        TEST_DB_PATH = None

    def test_successful_insert(self):
        # Parse_function returns a valid non-empty DataFrame
        def parse_fn(pre_text):
            return pd.DataFrame([{"Date_utc": "2025-10-09T00:00:00Z", "station": "100", "value": 1.23}])

        fetch_parse_store("100", "t", parse_fn, "test_table")

        # Verify record inserted
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM test_table WHERE Date_utc = ? AND station = ?", ("2025-10-09T00:00:00Z", "100")).fetchone()[0]
        self.assertEqual(count, 1)
        # Logger recorded success messages
        self.assertTrue(any("Successfully processed test_table (station 100)." in m for m in logger.infos))

    def test_empty_dataframe_no_insert(self):
        def parse_fn(pre_text):
            return pd.DataFrame(columns=["Date_utc", "station", "value"])  # empty

        fetch_parse_store("100", "t", parse_fn, "test_table")

        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM test_table WHERE station = ?", ("100",)).fetchone()[0]
        self.assertEqual(count, 0)
        self.assertTrue(any("Parsed DataFrame is empty" in m for m in logger.warnings))

    def test_missing_required_columns(self):
        # Missing "station" column
        def parse_fn(pre_text):
            return pd.DataFrame([{"Date_utc": "2025-10-09T00:00:00Z", "value": 2.34}])

        fetch_parse_store("100", "t", parse_fn, "test_table")

        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM test_table WHERE Date_utc = ?", ("2025-10-09T00:00:00Z",)).fetchone()[0]
        self.assertEqual(count, 0)
        self.assertTrue(any("Validation failed: Missing required columns" in m for m in logger.errors))

    def test_skip_duplicate(self):
        # Insert an initial record
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO test_table (Date_utc, station, value) VALUES (?, ?, ?)",
                         ("2025-10-09T00:00:00Z", "100", 9.99))
            conn.commit()

        def parse_fn(pre_text):
            return pd.DataFrame([{"Date_utc": "2025-10-09T00:00:00Z", "station": "100", "value": 9.99}])

        fetch_parse_store("100", "t", parse_fn, "test_table")

        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM test_table WHERE Date_utc = ? AND station = ?",
                                 ("2025-10-09T00:00:00Z", "100")).fetchone()[0]
        # Should remain 1 (no duplicate inserted)
        self.assertEqual(count, 1)
        self.assertTrue(any("Skipping duplicate entry" in m for m in logger.infos))

    def test_database_error_propagates_and_is_logged(self):
        # Make parse_fn produce valid DataFrame, but we'll create a table with a NOT NULL constraint to force DB error
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DROP TABLE IF EXISTS bad_table")
            conn.execute(
                """
                CREATE TABLE bad_table (
                    Date_utc TEXT NOT NULL,
                    station TEXT NOT NULL,
                    value REAL NOT NULL
                )
                """
            )
            # Intentionally create a schema mismatch by removing 'value' column later simulated by insert constraints.
            conn.commit()

        # Produce a row missing 'value' to violate NOT NULL
        def parse_fn(pre_text):
            return pd.DataFrame([{"Date_utc": "2025-10-09T00:00:00Z", "station": "100"}])

        # Patch the connection object returned by get_connection
        with mock.patch("sqlite3.connect") as mock_connect:
            real_conn = sqlite3.connect(self.db_path)
            mock_connect.return_value = real_conn

            with mock.patch.object(real_conn, "executemany", side_effect=sqlite3.OperationalError("simulated DB failure")):
                fetch_parse_store("100", "t", parse_fn, "bad_table")
        
        # Verify error was logged
        self.assertTrue(any("Database error while processing bad_table (station 100)" in m for m in logger.errors))

if __name__ == "__main__":
    unittest.main()

# Created with AI assistance
