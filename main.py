import logging
from src.storage import get_connection, load_ddl, init_db
from scheduler import scheduler

logger = logging.getLogger(__name__)

def main():
    logger.info("✅ Container startup -- initializing DB")
    engine = get_connection()
    try:
        init_db(engine)
        logger.info("Starting the scheduler...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("❌ Shutdown signal received")

if __name__ == "__main__":
    main()
