from datetime import datetime, timedelta
from collections import defaultdict
from typing import List
from django.db.models import Q
from asgiref.sync import sync_to_async
from calendar import monthrange
from event.models import Event
from user.models import User
from bot.locale.utils import t
import logging

logger = logging.getLogger("event")


async def create_event(
    *,
    user: User,
    name: str,
    date_time: datetime,
    periodicity: str,
    reminder_minutes: int,
    category: str,
    tags: str,
) -> Event:
    """Create an event after checking for time conflicts."""
    if await has_conflict(user, date_time):
        raise ValueError(t("event_conflict", user.language))

    event = await sync_to_async(Event.objects.create)(
        user=user,
        name=name,
        date_time=date_time,
        periodicity=periodicity,
        reminder_minutes=reminder_minutes,
        category=category,
        tags=tags,
    )
    logger.info(f"Created event for {user.telegram_id}: {event}")
    return event


async def create_event_without_conflict_check(**kwargs) -> Event:
    """Create an event directly (e.g. for import), without checking conflicts."""
    return await sync_to_async(Event.objects.create)(**kwargs)


async def get_events_for_today(user: User) -> List[Event]:
    """Return all events scheduled for today."""
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return await sync_to_async(list)(
        Event.objects.filter(
            user=user, date_time__gte=start, date_time__lt=end
        ).order_by("date_time")
    )


async def get_events_for_week(user: User) -> List[Event]:
    """Return events for the next 7 days."""
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    return await sync_to_async(list)(
        Event.objects.filter(
            user=user, date_time__gte=start, date_time__lt=end
        ).order_by("date_time")
    )


async def analyze_user_load(user: User, days_ahead: int = 7, threshold: int = 5) -> str:
    """Analyze user's load for the next few days."""
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=days_ahead)

    events = await sync_to_async(list)(
        Event.objects.filter(user=user, date_time__gte=start, date_time__lt=end)
    )

    daily_counts = defaultdict(int)
    for event in events:
        day = event.date_time.date()
        daily_counts[day] += 1

    overloaded = {
        day: count for day, count in daily_counts.items() if count > threshold
    }

    if not overloaded:
        return t("analyze_ok", user.language)

    lines = [t("analyze_overload", user.language)]
    for day, count in sorted(overloaded.items()):
        lines.append(f"{day.strftime('%Y-%m-%d')}: {count}")
    return "\n".join(lines)


async def get_events_for_month(user: User) -> list[Event]:
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    _, last_day = monthrange(now.year, now.month)
    end = start.replace(day=last_day, hour=23, minute=59, second=59)

    return await sync_to_async(list)(
        Event.objects.filter(
            user=user, date_time__gte=start, date_time__lte=end
        ).order_by("date_time")
    )


async def has_conflict(
    user: User, date_time: datetime, buffer_minutes: int = 30
) -> bool:
    """Check if there are any events close to given time (± buffer)."""
    start = date_time - timedelta(minutes=buffer_minutes)
    end = date_time + timedelta(minutes=buffer_minutes)
    return await sync_to_async(
        Event.objects.filter(user=user, date_time__gte=start, date_time__lte=end).exists
    )()
