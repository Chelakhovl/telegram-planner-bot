from datetime import datetime, timedelta
from collections import defaultdict

from event.models import Event
from user.models import User
from bot.locale.utils import t


def analyze_user_load(user: User, days_ahead: int = 7, threshold: int = 5) -> str:
    """
    Analyze how many events are scheduled in the next `days_ahead` days.
    Return warning if any day exceeds `threshold` events.
    """
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=days_ahead)

    events = Event.objects.filter(user=user, date_time__gte=start, date_time__lt=end)

    daily_counts = defaultdict(int)
    for event in events:
        day = event.date_time.date()
        daily_counts[day] += 1

    overloaded_days = {
        day: count for day, count in daily_counts.items() if count > threshold
    }

    lang = user.language

    if not overloaded_days:
        return t("analyze_ok", lang)

    result = [t("analyze_overload", lang)]
    for day, count in sorted(overloaded_days.items()):
        result.append(f"{day.strftime('%Y-%m-%d')}: {count}")
    return "\n".join(result)
