import logging
from sqlalchemy import MetaData, Table, select, func, and_
from src.fetch_data import fetch_pre_text, build_url
from src.parse_table import parse_cdip_pre_mp, parse_cdip_pre_te, parse_cdip_pre_9c, parse_cdip_jdar_wind
from src.db_utils import prepare_df_for_db, scalar_for_db
from src.storage import get_connection
from src.config import STATIONS, USE_POSTGRES

logger = logging.getLogger(__name__)
ALLOWED_TABLES = {"wind", "swell", "temps", "energy"}

def fetch_parse_store(station, table, parse_function, table_name, justdar: bool = False, timeout: int = 10):
    """Fetch data from URL, validate it, and store it in the database using SQLAlchemy Core."""
    try:
        if table_name not in ALLOWED_TABLES:
            logger.error(f"Invalid table name: {table_name}")
            return

        url = build_url(station, table, justdar=justdar)
        logger.info(f"Fetching data for {table_name} (station {station})...")
        pre_text = fetch_pre_text(url, timeout=timeout)

        logger.info(f"Parsing data for {table_name} (station {station})...")
        df = parse_function(pre_text)

        if df.empty:
            logger.warning(f"❌ No data to insert for {table_name} (station {station}). Parsed DataFrame is empty.")
            return

        # Validate parsed data
        required_columns = {"date_utc", "station"}
        if not required_columns.issubset(df.columns):
            logger.error(f"❌ Validation failed: Missing required columns in parsed data for {table_name} (station {station}).")
            return

        engine = get_connection()
        metadata = MetaData()

        df = prepare_df_for_db(df, engine)

        # Reflect only the target table to avoid reflecting whole DB
        table_obj = Table(table_name, metadata, autoload_with=engine)

        # Check for an existing row using SQLAlchemy Core
        row_date = scalar_for_db(df["date_utc"].iloc[0], engine, kind ="date")
        row_station = int(df["station"].iloc[0])
        count_expr = func.count()
        check_stmt = select(count_expr).select_from(table_obj).where(
            and_(
                table_obj.c.time_utc == row_date,
                table_obj.c.station == row_station
            )
        )

        try:
            with engine.connect() as conn:
                existing_count = conn.execute(check_stmt).scalar()
                if existing_count and existing_count > 0:
                    logger.info(f"Skipping duplicate entry for {table_name} (station {station}).")
                    return

                logger.info(f"Storing data for {table_name} (station {station})...")
                # Use pandas to_sql to append rows
                df.to_sql(table_name, engine, if_exists="append", index=False)
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
