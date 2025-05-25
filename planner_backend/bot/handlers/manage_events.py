from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from datetime import datetime, timedelta
from asgiref.sync import sync_to_async

from user.services import get_or_create_user
from event.models import Event
from bot.locale.utils import t

router = Router()


class EditEventStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_new_value = State()


@router.message(Command("my_events"))
async def show_events(message: Message):
    """
    Show upcoming events for the next 7 days with edit/delete options.
    """
    user = await get_or_create_user(message.from_user.id)
    now = datetime.now()
    future = now + timedelta(days=7)

    events = await sync_to_async(list)(
        Event.objects.filter(
            user=user, date_time__gte=now, date_time__lt=future
        ).order_by("date_time")
    )

    if not events:
        await message.answer(t("no_upcoming_events", user.language))
        return

    for event in events:
        kb = InlineKeyboardBuilder()
        kb.button(text="Edit", callback_data=f"edit_{event.id}")
        kb.button(text="Delete", callback_data=f"delete_{event.id}")
        await message.answer(
            f"{event.name}\n{event.date_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"{event.category} | {event.periodicity} | reminder {event.reminder_minutes} min\n"
            f"Tags: {event.tags}",
            reply_markup=kb.as_markup(),
        )


@router.callback_query(F.data.startswith("delete_"))
async def delete_event(callback: CallbackQuery):
    """
    Delete selected event.
    """
    event_id = callback.data.split("_")[1]
    user = await get_or_create_user(callback.from_user.id)

    try:
        event = await sync_to_async(Event.objects.get)(id=event_id)
        await sync_to_async(event.delete)()
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(t("event_deleted", user.language))
    except Event.DoesNotExist:
        await callback.message.answer(t("event_not_found", user.language))
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("edit_"))
async def start_edit(callback: CallbackQuery, state: FSMContext):
    """
    Start editing process: choose a field.
    """
    event_id = callback.data.split("_")[1]
    await state.update_data(event_id=event_id)

    kb = InlineKeyboardBuilder()
    for field in [
        "name",
        "date_time",
        "periodicity",
        "reminder_minutes",
        "category",
        "tags",
    ]:
        kb.button(text=field, callback_data=f"field_{field}")

    user = await get_or_create_user(callback.from_user.id)
    await callback.message.answer(
        t("select_field_edit", user.language), reply_markup=kb.as_markup()
    )
    await state.set_state(EditEventStates.waiting_for_field)
    await callback.answer()


@router.callback_query(EditEventStates.waiting_for_field, F.data.startswith("field_"))
async def ask_for_value(callback: CallbackQuery, state: FSMContext):
    """
    Ask user to enter new value for selected field.
    """
    field = callback.data.split("_", 1)[1]
    await state.update_data(field_to_edit=field)

    user = await get_or_create_user(callback.from_user.id)
    await callback.message.answer(f"{t('enter_new_value', user.language)} {field}:")
    await state.set_state(EditEventStates.waiting_for_new_value)
    await callback.answer()


@router.message(EditEventStates.waiting_for_new_value)
async def save_new_value(message: Message, state: FSMContext):
    """
    Save updated value to event.
    """
    data = await state.get_data()
    user = await get_or_create_user(message.from_user.id)
    event_id = data["event_id"]
    field = data["field_to_edit"]
    new_value = message.text

    try:
        event = await sync_to_async(Event.objects.get)(id=event_id)

        if field == "date_time":
            try:
                new_value = datetime.strptime(new_value, "%Y-%m-%d %H:%M")
            except ValueError:
                await message.answer("Invalid datetime format. Use YYYY-MM-DD HH:MM")
                return
        elif field == "reminder_minutes":
            if not new_value.isdigit():
                await message.answer("Reminder must be a number.")
                return
            new_value = int(new_value)

        setattr(event, field, new_value)
        await sync_to_async(event.save)()
        await message.answer(t("event_updated", user.language))

    except Exception as e:
        await message.answer(t("invalid_update", user.language).format(error=str(e)))
    finally:
        await state.clear()


@router.message(Command("clear"))
async def clear_all_events(message: Message):
    user = await get_or_create_user(message.from_user.id)
    await sync_to_async(Event.objects.filter(user=user).delete)()
    await message.answer(t("cleared", user.language))
