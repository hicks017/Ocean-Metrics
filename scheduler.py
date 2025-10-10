from datetime import datetime, timedelta
import logging
from threading import Lock
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from tasks import task_fetch_wind, task_fetch_swell, task_fetch_temps, task_fetch_energy

logger = logging.getLogger("scheduler")
logging.basicConfig(level=logging.INFO)

# A simple lock to serialize database writes when tasks share the same database connection
db_lock = Lock()
def safe_wrap(task_func, *, lock_db=True):
    """
    Wrap a task so it acquires the database lock while running critical section.
    Use this if tasks perform non-threadsafe database operations or share a single connection.
    """
    def wrapper():
        start = datetime.utcnow()
        logger.info("Starting %s at %s", task_func.__name__, start.isoformat())
        try:
            if lock_db:
                with db_lock:
                    task_func()
            else:
                task_func()
            logger.info("Finished %s at %s", task_func.__name__, datetime.utcnow().isoformat())
        except Exception:
            logger.exception("Error running %s", task_func.__name__)
    return wrapper

# Force single worker (fully serialized)
executors = {"default": ThreadPoolExecutor(1)}
scheduler = BlockingScheduler(executors=executors)

# Schedule tasks and run all tasks immediately, one after another because only one worker exists
base = datetime.utcnow() + timedelta(seconds=1) # Avoids tiny past timestamps
scheduler.add_job(safe_wrap(task_fetch_wind), "interval", hours=1, next_run_time=base, max_instances=1, misfire_grace_time=30, coalesce=True)
scheduler.add_job(safe_wrap(task_fetch_swell), "interval", hours=1, next_run_time=base, max_instances=1, misfire_grace_time=30, coalesce=True)
scheduler.add_job(safe_wrap(task_fetch_temps), "interval", hours=1, next_run_time=base, max_instances=1, misfire_grace_time=30, coalesce=True)
scheduler.add_job(safe_wrap(task_fetch_energy), "interval", hours=1, next_run_time=base, max_instances=1, misfire_grace_time=30, coalesce=True)

if __name__ == "__main__":
    print("Starting scheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")

# Created with AI assistance
