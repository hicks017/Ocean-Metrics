import logging
from src.fetch_data import fetch_pre_text, build_url
from src.parse_table import parse_cdip_pre_mp, parse_cdip_pre_te, parse_cdip_pre_9c, parse_cdip_jdar_wind
from src.storage import get_connection
from src.config import STATIONS

logger = logging.getLogger(__name__)

def fetch_parse_store(station, table, parse_function, table_name):
    """Fetch data from URL, parse it, and store it in the database."""
    try:
        url = build_url(station, table)
        logger.info(f"Fetching data for {table_name} (station {station})...")
        pre_text = fetch_pre_text(url)
        logger.info(f"Parsing data for {table_name} (station {station})...")
        df = parse_function(pre_text)

        # Check for duplicates before inserting
        with get_connection() as conn:
            existing_records = conn.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE Date_utc = ? AND station = ?",
                (df['Date_utc'].iloc[0], station)
            ).fetchone()[0]

            if existing_records > 0:
                logger.info(f"Skipping duplicate entry for {table_name} (station {station}).")
                return

            logger.info(f"Storing data for {table_name} (station {station})...")
            df.to_sql(table_name, conn, if_exists="append", index=False)
        logger.info(f"Successfully processed {table_name} (station {station}).")
    except Exception as e:
        logger.error(f"Error processing {table_name} (station {station}): {e}")

def task_fetch_wind():
    for station in STATIONS["wind"]:
        fetch_parse_store(station, "wind", parse_cdip_jdar_wind, "wind")

def task_fetch_swell():
    for station in STATIONS["swell"]:
        fetch_parse_store(station, "swell", parse_cdip_pre_mp, "swell")

def task_fetch_temps():
    for station in STATIONS["temps"]:
        fetch_parse_store(station, "temps", parse_cdip_pre_te, "temps")

def task_fetch_energy():
    for station in STATIONS["energy"]:
        fetch_parse_store(station, "energy", parse_cdip_pre_9c, "energy")