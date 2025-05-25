import csv
from datetime import datetime, timedelta
from event.models import Event
from user.models import User
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger("event")

# CSV field mapping
CSV_FIELDS = [
    "Назва",
    "Дата і час",
    "Періодичність",
    "Нагадування (хв)",
    "Категорія",
    "Теги",
]


@sync_to_async
def _create_event_from_row(row: dict, user: User) -> bool:
    try:
        Event.objects.create(
            user=user,
            name=row["Назва"],
            date_time=datetime.strptime(row["Дата і час"], "%Y-%m-%d %H:%M"),
            periodicity=row["Періодичність"],
            reminder_minutes=int(row["Нагадування (хв)"]),
            category=row["Категорія"],
            tags=row["Теги"],
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to import event row: {row} | Error: {e}")
        return False


async def import_from_csv(file_path: str, user: User) -> tuple[int, int]:
    """Import events from CSV. Returns (success_count, error_count)."""
    success, errors = 0, 0

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ok = await _create_event_from_row(row, user)
            if ok:
                success += 1
            else:
                errors += 1

    return success, errors


async def export_to_csv(file_path: str, user: User, days: int = 30) -> int:
    """Export user's events to CSV. Returns number of exported events."""
    now = datetime.now()
    events = await sync_to_async(list)(
        Event.objects.filter(
            user=user, date_time__gte=now - timedelta(days=days)
        ).order_by("date_time")
    )

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_FIELDS)

        for event in events:
            writer.writerow(
                [
                    event.name,
                    event.date_time.strftime("%Y-%m-%d %H:%M"),
                    event.periodicity,
                    event.reminder_minutes,
                    event.category,
                    event.tags,
                ]
            )
        file.flush()

    return len(events)
