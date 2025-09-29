import os

# Configuration ------------------------------------------------------------------------
SQLITE_FILE = "data/data.sqlite3"
POSTGRES_VARS = {
    "host":     os.getenv("PG_HOST"),
    "port":     os.getenv("PG_PORT"),
    "user":     os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "dbname":   os.getenv("PG_DB")
}
USE_POSTGRES = all(POSTGRES_VARS.values())
