from aiogram import Router, F
from aiogram.types import Message, Document
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import tempfile
import os
import logging

from user.services import get_or_create_user
from event.io import import_from_csv
from bot.locale.utils import t

router = Router()
logger = logging.getLogger(__name__)


class ImportStates(StatesGroup):
    waiting_for_file = State()


@router.message(Command("import"))
async def start_import(message: Message, state: FSMContext):
    user = await get_or_create_user(message.from_user.id)
    await message.answer(t("send_csv_file", user.language))
    await state.set_state(ImportStates.waiting_for_file)


@router.message(ImportStates.waiting_for_file, F.document)
async def handle_csv_file(message: Message, document: Document, state: FSMContext):
    user = await get_or_create_user(message.from_user.id)

    if not document.file_name.lower().endswith(".csv"):
        await message.answer(t("wrong_file_format", user.language))
        return

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    file_path = temp_file.name
    temp_file.close()

    try:
        await document.download(destination_file=file_path)

        success, errors = await import_from_csv(file_path, user)
        await message.answer(
            t("import_summary", user.language).format(success=success, errors=errors)
        )

    except Exception as e:
        logger.exception("Import failed")
        await message.answer(t("import_failed", user.language))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        await state.clear()
