import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from src.config import SQLITE_FILE, POSTGRES_VARS, USE_POSTGRES

ROOT = Path(__file__).resolve().parent.parent

# Configure simple console logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_connection() -> Engine:
    """
    Returns a SQLAlchemy Engine for either Postgres or SQLite.
    """
    if USE_POSTGRES:
        url = f"postgresql://{POSTGRES_VARS['user']}:{POSTGRES_VARS['password']}@{POSTGRES_VARS['host']}:{POSTGRES_VARS['port']}/{POSTGRES_VARS['dbname']}"
        return create_engine(url, poolclass=NullPool, isolation_level='AUTOCOMMIT')
    return create_engine(f'sqlite:///{SQLITE_FILE}', poolclass=NullPool)

def load_ddl(table_name: str, dialect: str) -> str:
    """
    Reads the external SQL database for a table.
    Assumes files named init_<table>.<dialetct>.sql under sql/.
    dialect: 'sqlite' or 'postgres'.
    """
    filename = f"init_table_{table_name}.postgres.sql" if dialect == "postgres" else f"init_table_{table_name}.sqlite.sql"
    sql_file = ROOT / "sql" / filename
    if not sql_file.exists():
        raise FileNotFoundError(f"DDL not found: {sql_file}")
    return sql_file.read_text()

def init_db(engine: Engine):
    """
    Creates tables (wind, swell, temps, energy) with date_utc,
    wraps each DDL/index in try/except.
    """
    tables = ["wind", "swell", "temps", "energy"]
    dialect = "postgres" if USE_POSTGRES else "sqlite"

    with engine.begin() as conn:  # begin a transaction
        for table in tables:
            # CREATE TABLE
            try:
                ddl = load_ddl(table, dialect)
                # Debugging: Log the SQL command being executed
                logging.debug(f"Executing SQL: {ddl}")
                conn.execute(text(ddl))
                logging.info(f"✅ Verified table: {table}")
            except Exception as e:
                logging.error(f"❌ Error creating table {table}: {e}")
                continue  # Skip to the next table if table creation fails

            # CREATE INDEXES on Date_utc and Station
            for col in ["date_utc", "station"]:
                idx = f"idx_{table}_{col}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx} ON {table}({col});"
                try:
                    conn.execute(text(sql))
                    logging.info(f"✅ Verified index: {idx}")
                except Exception as e:
                    logging.error(f"❌ Error creating index {idx}: {e}")

# def main():
#     """
#     Entry point: open connection, init schema, auto-close.
#     """
#     with get_connection() as conn:
#         init_db(conn)

# if __name__ == "__main__":
#     main()

# Created with AI assistance
