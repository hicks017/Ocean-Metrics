import logging
import sqlite3
import psycopg
from pathlib import Path

from src.config import SQLITE_FILE, POSTGRES_VARS, USE_POSTGRES

ROOT = Path(__file__).resolve().parent.parent

# Configure simple console logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_connection():
    """
    Returns a DB connection to Postgres or SQLite.
    Supports use in 'with' for automatic close().
    """
    if USE_POSTGRES:
        return psycopg.connect(**POSTGRES_VARS)
    return sqlite3.connect(SQLITE_FILE)

def load_ddl(table_name: str) -> str:
    """
    Reads the external SQL file for a table.
    Assumes files named init_<table>.sql under project/sql/.
    """
    sql_file = ROOT / "sql" / f"init_table_{table_name}.sql"
    if not sql_file.exists():
        raise FileNotFoundError(f"DDL not found: {sql_file}")
    return sql_file.read_text()

def init_db(conn):
    """
    Creates tables (wind, swell, temps, energy) with Date_utc,
    wraps each DDL/index in try/except, then commits once.
    """
    cursor = conn.cursor()
    id_def = "SERIAL PRIMARY KEY" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    tables = ["wind", "swell", "temps", "energy"]

    for table in tables:
        # CREATE TABLE
        try:
            ddl = load_ddl(table).format(id_def=id_def)
            # Debugging: Log the SQL command being executed
            logging.debug(f"Executing SQL: {ddl}")
            cursor.execute(ddl)
            logging.info(f"✅ Verified table: {table}")
        except Exception as e:
            logging.error(f"❌ Error creating table {table}: {e}")
            continue  # Skip to the next table if table creation fails

        # CREATE INDEXES on Date_utc and Station
        for col in ["Date_utc", "station"]:
            idx = f"idx_{table}_{col.lower()}"
            sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col});"
            try:
                cursor.execute(sql)
                logging.info(f"✅ Verified index: {idx}")
            except Exception as e:
                logging.error(f"❌ Error creating index {idx}: {e}")

    try:
        conn.commit()
    except Exception as commit_error:
        logging.error(f"❌ Error during commit: {commit_error}")
        raise

# def main():
#     """
#     Entry point: open connection, init schema, auto-close.
#     """
#     with get_connection() as conn:
#         init_db(conn)

# if __name__ == "__main__":
#     main()

# Created with AI assistance
