from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from user.services import get_or_create_user
from event.services import (
    get_events_for_today,
    get_events_for_week,
    analyze_user_load,
    get_events_for_month,
)
from bot.locale.utils import t

router = Router()


@router.message(Command("today"))
async def view_today_events(message: Message):
    """
    Show events for today.
    """
    user = await get_or_create_user(message.from_user.id)
    events = await get_events_for_today(user)

    if not events:
        await message.answer(t("no_events_today", user.language))
        return

    lines = [t("today_events_title", user.language)]
    for event in sorted(events, key=lambda e: e.date_time):
        lines.append(
            f"{event.date_time.strftime('%H:%M')} — {event.name} ({event.category})"
        )

    await message.answer("\n".join(lines))


@router.message(Command("week"))
async def view_week_events(message: Message):
    """
    Show all events for the upcoming week, grouped by day.
    """
    user = await get_or_create_user(message.from_user.id)
    events = await get_events_for_week(user)

    if not events:
        await message.answer(t("no_events_week", user.language))
        return

    grouped = {}
    for event in events:
        day = event.date_time.strftime("%Y-%m-%d")
        grouped.setdefault(day, []).append(event)

    lines = [t("week_events_title", user.language)]
    for day in sorted(grouped.keys()):
        lines.append(f"\n{day}:")
        for event in sorted(grouped[day], key=lambda e: e.date_time):
            lines.append(
                f"{event.date_time.strftime('%H:%M')} — {event.name} ({event.category})"
            )

    await message.answer("\n".join(lines))


@router.message(Command("month"))
async def view_month_events(message: Message):
    user = await get_or_create_user(message.from_user.id)
    events = await get_events_for_month(user)

    if not events:
        await message.answer(t("no_events_month", user.language))
        return

    grouped = {}
    for event in events:
        day = event.date_time.strftime("%Y-%m-%d")
        grouped.setdefault(day, []).append(event)

    text = f"{t('month_events_title', user.language)}\n"
    for day, evts in grouped.items():
        text += f"\n{day}:\n"
        for e in evts:
            text += f"{e.date_time.strftime('%H:%M')} — {e.name} ({e.category})\n"

    await message.answer(text)


@router.message(Command("analyze"))
async def analyze_schedule(message: Message):
    """
    Analyze user's schedule load and return suggestions or summary.
    """
    user = await get_or_create_user(message.from_user.id)
    result = await analyze_user_load(user)
    await message.answer(result)
