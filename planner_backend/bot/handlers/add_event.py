from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from datetime import datetime
from user.services import get_or_create_user
from event.services import create_event
from bot.locale.utils import t

router = Router()


class AddEventStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_datetime = State()
    waiting_for_periodicity = State()
    waiting_for_reminder = State()
    waiting_for_category = State()
    waiting_for_tags = State()


def periodicity_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="once"), KeyboardButton(text="daily")],
            [
                KeyboardButton(text="weekly"),
                KeyboardButton(text="monthly"),
                KeyboardButton(text="yearly"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


@router.message(Command("add_event"))
async def add_event_start(message: Message, state: FSMContext):
    """
    Start the event creation process.
    """
    user = await get_or_create_user(message.from_user.id)
    await message.answer(t("add_event_prompt", user.language))
    await state.set_state(AddEventStates.waiting_for_name)


@router.message(AddEventStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """
    Store event name and request datetime.
    """
    await state.update_data(name=message.text)
    await message.answer("Enter date and time (format: 2025-05-25 14:30):")
    await state.set_state(AddEventStates.waiting_for_datetime)


@router.message(AddEventStates.waiting_for_datetime)
async def process_datetime(message: Message, state: FSMContext):
    """
    Store event datetime and request periodicity.
    """
    try:
        date_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        if date_time < datetime.now():
            await message.answer("Date cannot be in the past. Try again.")
            return
        await state.update_data(date_time=date_time)
        await message.answer("Select periodicity:", reply_markup=periodicity_keyboard())
        await state.set_state(AddEventStates.waiting_for_periodicity)
    except ValueError:
        await message.answer("Invalid format. Example: 2025-05-25 14:30")


@router.message(AddEventStates.waiting_for_periodicity)
async def process_periodicity(message: Message, state: FSMContext):
    """
    Store event periodicity and request reminder time.
    """
    value = message.text.lower()
    valid = ["once", "daily", "weekly", "monthly", "yearly"]
    if value not in valid:
        await message.answer("Choose one of: once, daily, weekly, monthly, yearly")
        return
    await state.update_data(periodicity=value)
    await message.answer(
        "How many minutes before the event to remind?",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddEventStates.waiting_for_reminder)


@router.message(AddEventStates.waiting_for_reminder)
async def process_reminder(message: Message, state: FSMContext):
    """
    Store reminder time and request category.
    """
    if not message.text.isdigit() or int(message.text) < 0:
        await message.answer("Enter a positive number of minutes:")
        return
    await state.update_data(reminder_minutes=int(message.text))
    await message.answer("Enter category (e.g., work, study):")
    await state.set_state(AddEventStates.waiting_for_category)


@router.message(AddEventStates.waiting_for_category)
async def process_category(message: Message, state: FSMContext):
    """
    Store category and request tags.
    """
    if len(message.text.strip()) < 2:
        await message.answer("Category is too short. Try again:")
        return
    await state.update_data(category=message.text.strip())
    await message.answer("Enter tags (comma-separated):")
    await state.set_state(AddEventStates.waiting_for_tags)


@router.message(AddEventStates.waiting_for_tags)
async def process_tags(message: Message, state: FSMContext):
    """
    Final step: create event and clear state.
    """
    data = await state.get_data()
    user = await get_or_create_user(message.from_user.id)

    event = await create_event(
        user=user,
        name=data["name"],
        date_time=data["date_time"],
        periodicity=data["periodicity"],
        reminder_minutes=data["reminder_minutes"],
        category=data["category"],
        tags=message.text,
    )

    summary = (
        f"Event created successfully:\n\n"
        f"Name: {event.name}\n"
        f"Date: {event.date_time.strftime('%Y-%m-%d %H:%M')}\n"
        f"Periodicity: {event.periodicity}\n"
        f"Reminder: {event.reminder_minutes} min before\n"
        f"Category: {event.category}\n"
        f"Tags: {message.text}"
    )

    await message.answer(summary)
    await state.clear()
