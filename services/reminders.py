from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pymongo import MongoClient
from datetime import datetime, timezone
import pytz
import uuid

from config import settings
from services.updater import run_full_update


mongo_client = MongoClient(settings.MONGODB_URI)
reminders_col = mongo_client[settings.MONGODB_DB][settings.REMINDER_COLLECTION]
updates_col = mongo_client[settings.MONGODB_DB][settings.UPDATES_COLLECTION]

jobstore = MongoDBJobStore(
    client=mongo_client,
    database=settings.MONGODB_DB,
    collection=settings.JOBSTORE_COLLECTION
)
scheduler = BackgroundScheduler(timezone=pytz.timezone("America/New_York"))
scheduler.add_jobstore(jobstore)

async def send_reminder(reminder_id: str):
    # TODO: implement notification logic (email/Telegram)
    pass


def init_scheduler():
    """
    Start scheduler and register existing reminders.
    Active jobs are resumed; inactive are paused.
    """
    print("Loading Reminders...")
    scheduler.start()
    for doc in reminders_col.find():
        job_id = doc["job_id"]
        try:
            if doc.get("active"):
                scheduler.resume_job(job_id)
            else:
                scheduler.pause_job(job_id)
        except Exception:
            continue

    update_doc = updates_col.find_one({"name": "prices"})
    if update_doc is None:
        u_id = uuid.uuid4().hex
        job = scheduler.add_job(
            func=run_full_update,
            trigger=CronTrigger(
                day_of_week="mon-fri",
                hour=16, minute=30,
                timezone="America/New_York"
            ),
            id=u_id
        )
        updates_col.insert_one({
            "_id": u_id,
            "name": "prices",
            "job_id": job.id
        })


def create_reminders_for_portfolio(portfolio_id: str, created_at: datetime):
    """
    Batch-create daily, weekly, and quarterly reminders for a portfolio.
    Jobs are scheduled then immediately paused (active=False).
    Returns list of inserted reminder documents.
    """
    triggers = {
        "daily": CronTrigger(
            day_of_week="mon-thu", hour=17, minute=0,
            timezone="America/New_York"
        ),
        "weekly": CronTrigger(
            day_of_week="fri", hour=17, minute=0,
            timezone="America/New_York"
        ),
        "quarterly": IntervalTrigger(
            weeks=13,
            start_date=created_at.astimezone(pytz.timezone("America/New_York"))
        ),
    }
    now = datetime.now(timezone.utc)
    docs = []
    for typ, trigger in triggers.items():
        rem_id = uuid.uuid4().hex
        job = scheduler.add_job(
            func=send_reminder,
            trigger=trigger,
            id=rem_id,
            args=[rem_id],
            replace_existing=True
        )
        scheduler.pause_job(rem_id)
        doc = {
            "_id": rem_id,
            "portfolio_id": portfolio_id,
            "type": typ,
            "job_id": job.id,
            "active": False,
            "created_at": now,
            "updated_at": now,
        }
        reminders_col.insert_one(doc)
        docs.append(doc)
    return docs


def toggle_reminder(reminder_id: str, active: bool) -> dict:
    """
    Pause or resume an existing reminder.
    Updates both APScheduler and the Mongo document.
    """
    doc = reminders_col.find_one({"_id": reminder_id})
    if not doc:
        raise ValueError("Reminder not found")
    job_id = doc["job_id"]
    if active:
        scheduler.resume_job(job_id)
    else:
        scheduler.pause_job(job_id)
    new_time = datetime.now(timezone.utc)
    updated = reminders_col.find_one_and_update(
        {"_id": reminder_id},
        {"$set": {"active": active, "updated_at": new_time}},
        return_document=True
    )
    return updated


def get_reminders_for_portfolio(portfolio_id: str) -> list:
    """
    Fetch all reminder documents for a given portfolio.
    """
    return list(reminders_col.find({"portfolio_id": portfolio_id}))