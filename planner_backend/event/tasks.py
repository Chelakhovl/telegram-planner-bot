import os
import logging
import asyncio
import subprocess
from datetime import datetime, timedelta
from celery import shared_task

from event.models import Event
from bot.main import bot

logger = logging.getLogger("event")


@shared_task
def check_reminders():
    """
    Check events due soon and send reminders.
    This function is synchronous but invokes async bot method via asyncio.
    """
    now = datetime.now()
    future = now + timedelta(hours=12)

    events = Event.objects.filter(
        date_time__gte=now, date_time__lt=future, notified=False
    )

    async def send_reminders():
        for event in events:
            remind_at = event.date_time - timedelta(minutes=event.reminder_minutes)
            if now >= remind_at:
                try:
                    await bot.send_message(
                        chat_id=event.user.telegram_id,
                        text=f"Нагадування: {event.name} о {event.date_time.strftime('%H:%M')}",
                    )
                    event.notified = True
                    event.save()
                    logger.info(
                        f"Reminder sent to {event.user.telegram_id} for event {event.name}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send reminder: {e}")

    try:
        asyncio.run(send_reminders())
    except RuntimeError:
        # fallback for existing event loop (e.g. if Celery is run with gevent)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_reminders())


@shared_task
def backup_and_cleanup_db(max_backups=7):
    """
    Create PostgreSQL backup and clean up old backups.
    """
    logger.info("Starting DB backup task...")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BACKUP_DIR = os.path.join(BASE_DIR, "backups")
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_file = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.sql")

    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    command = [
        "pg_dump",
        "-h",
        DB_HOST,
        "-p",
        DB_PORT,
        "-U",
        DB_USER,
        "-F",
        "p",
        "-d",
        DB_NAME,
        "-f",
        backup_file,
    ]

    try:
        subprocess.run(command, env=env, check=True)
        logger.info(f"Backup created: {backup_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e}")
        return

    # Clean up old backups
    backups = sorted(
        [
            os.path.join(BACKUP_DIR, f)
            for f in os.listdir(BACKUP_DIR)
            if f.endswith(".sql")
        ],
        key=os.path.getmtime,
    )

    while len(backups) > max_backups:
        old = backups.pop(0)
        os.remove(old)
        logger.info(f"Old backup removed: {old}")
