import logging
from src.fetch_data import fetch_pre_text, build_url
from src.parse_table import parse_cdip_pre_mp, parse_cdip_pre_te, parse_cdip_pre_9c, parse_cdip_jdar_wind
from src.storage import get_connection

logger = logging.getLogger(__name__)

def fetch_parse_store(station, table, parse_function, table_name):
    """Fetch data from URL, parse it, and store it in the database."""
    try:
        url = build_url(station, table)
        logger.info(f"Fetching data for {table_name}...")
        pre_text = fetch_pre_text(url)
        logger.info(f"Parsing data for {table_name}...")
        df = parse_function(pre_text)

        # Check for duplicates before inserting
        with get_connection() as conn:
            existing_records = conn.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE Date_utc = ? AND station = ?",
                (df['Date_utc'].iloc[0], station)
            ).fetchone()[0]

            if existing_records > 0:
                logger.info(f"Skipping duplicate entry for {table_name}.")
                return

            logger.info(f"Storing data for {table_name}...")
            df.to_sql(table_name, conn, if_exists="append", index=False)
        logger.info(f"Successfully processed {table_name}.")
    except Exception as e:
        logger.error(f"Error processing {table_name}: {e}")

def task_fetch_wind():
    fetch_parse_store("100", "wind", parse_cdip_jdar_wind, "wind")

def task_fetch_swell():
    fetch_parse_store("100", "swell", parse_cdip_pre_mp, "swell")

def task_fetch_temps():
    fetch_parse_store("100", "temps", parse_cdip_pre_te, "temps")

def task_fetch_energy():
    fetch_parse_store("100", "energy", parse_cdip_pre_9c, "energy")