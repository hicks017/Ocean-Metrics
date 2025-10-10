from apscheduler.schedulers.blocking import BlockingScheduler
from tasks import task_fetch_wind, task_fetch_swell, task_fetch_temps, task_fetch_energy

scheduler = BlockingScheduler()

# Schedule tasks
scheduler.add_job(task_fetch_wind, "interval", hours=1)
scheduler.add_job(task_fetch_swell, "interval", hours=1)
scheduler.add_job(task_fetch_temps, "interval", hours=1)
scheduler.add_job(task_fetch_energy, "interval", hours=1)

if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler.start()