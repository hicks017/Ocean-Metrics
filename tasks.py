import logging
from src.fetch_data import fetch_pre_text, build_url
from src.parse_table import parse_cdip_pre_mp, parse_cdip_pre_te, parse_cdip_pre_9c, parse_cdip_jdar_wind
from src.storage import get_connection
from src.config import STATIONS, USE_POSTGRES

logger = logging.getLogger(__name__)

def fetch_parse_store(station, table, parse_function, table_name, justdar: bool = False, timeout: int = 10):
    """Fetch data from URL, validate it, and store it in the database."""
    try:
        url = build_url(station, table, justdar=justdar)
        logger.info(f"Fetching data for {table_name} (station {station})...")
        pre_text = fetch_pre_text(url, timeout=timeout)
        logger.info(f"Parsing data for {table_name} (station {station})...")
        df = parse_function(pre_text)

        if df.empty:
            logger.warning(f"❌ No data to insert for {table_name} (station {station}). Parsed DataFrame is empty.")
            return

        # Validate parsed data
        required_columns = ["Date_utc", "station"]
        if not all(col in df.columns for col in required_columns):
            logger.error(f"❌ Validation failed: Missing required columns in parsed data for {table_name} (station {station}).")
            return

        # Check for duplicates before inserting
        with get_connection() as conn:
            try:
                placeholder = '%s' if USE_POSTGRES else '?'
                existing_records = conn.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE Date_utc = {placeholder} AND station = {placeholder}",
                    (val_date, station)
                ).fetchone()[0]

                if existing_records > 0:
                    logger.info(f"Skipping duplicate entry for {table_name} (station {station}).")
                    return

                logger.info(f"Storing data for {table_name} (station {station})...")
                df.to_sql(table_name, conn, if_exists="append", index=False)
            except Exception as db_error:
                logger.error(f"❌ Database error while processing {table_name} (station {station}): {db_error}")
                raise
        logger.info(f"✅ Successfully processed {table_name} (station {station}).")
    except Exception as e:
        logger.error(f"❌ Error processing {table_name} (station {station}): {e}")

def task_fetch_wind():
    for station in STATIONS["wind"]:
        fetch_parse_store(station, "pm", parse_cdip_jdar_wind, "wind", justdar=True, timeout=30)

def task_fetch_swell():
    for station in STATIONS["swell"]:
        fetch_parse_store(station, "mp", parse_cdip_pre_mp, "swell")

def task_fetch_temps():
    for station in STATIONS["temps"]:
        fetch_parse_store(station, "te", parse_cdip_pre_te, "temps")

def task_fetch_energy():
    for station in STATIONS["energy"]:
        fetch_parse_store(station, "9c", parse_cdip_pre_9c, "energy")

# Created with AI assistance
