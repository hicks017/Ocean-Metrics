import os

# Configuration ------------------------------------------------------------------------

# Database settings with no defaults
SQLITE_FILE = "data/data.sqlite3"
POSTGRES_VARS = {
    "host":     os.getenv("PG_HOST"),
    "port":     os.getenv("PG_PORT"),
    "user":     os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "dbname":   os.getenv("PG_DB")
}
USE_POSTGRES = all(POSTGRES_VARS.values())

# Fetch stations, use defaults if none are provided
STATIONS = {
    "wind": os.getenv("WIND", "73").split(","),
    "swell": os.getenv("SWELL", "100").split(","),
    "temps": os.getenv("TEMPS", "100").split(","),
    "energy": os.getenv("ENERGY", "100").split(",")
}
