from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
import logging

logger = logging.getLogger("event")


def create_periodic_task():
    """
    Create or enable periodic Celery tasks:
    - Reminder check every 1 minute
    - DB backup every 1 day
    """

    minute_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1, period=IntervalSchedule.MINUTES
    )

    reminder_task, created = PeriodicTask.objects.get_or_create(
        name="Check event reminders",
        defaults={
            "interval": minute_schedule,
            "task": "event.tasks.check_reminders",
            "args": json.dumps([]),
            "enabled": True,
        },
    )

    if not created:
        reminder_task.enabled = True
        reminder_task.interval = minute_schedule
        reminder_task.save()

    logger.info("Reminder task registered or updated.")

    daily_schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1, period=IntervalSchedule.DAYS
    )

    backup_task, created = PeriodicTask.objects.get_or_create(
        name="Backup DB daily",
        defaults={
            "interval": daily_schedule,
            "task": "event.tasks.backup_and_cleanup_db",
            "args": json.dumps([]),
            "enabled": True,
        },
    )

    if not created:
        backup_task.enabled = True
        backup_task.interval = daily_schedule
        backup_task.save()

    logger.info("Backup task registered or updated.")
