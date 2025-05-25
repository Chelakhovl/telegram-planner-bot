from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
import tempfile
import os
import logging

from user.services import get_or_create_user
from event.io import export_to_csv
from bot.locale.utils import t

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("export"))
async def export_csv(message: Message):
    """
    Export user's events to a CSV file and send it to the user.
    """
    user = await get_or_create_user(message.from_user.id)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    file_path = tmp_file.name
    tmp_file.close()

    try:
        count = await export_to_csv(file_path, user)

        if count == 0:
            await message.answer(t("no_events_to_export", user.language))
            return

        filename = f"events_{user.telegram_id}.csv"
        await message.answer_document(
            FSInputFile(file_path, filename=filename),
            caption=t("export_done", user.language).format(count=count),
        )

    except Exception as e:
        logger.exception("Export failed")
        await message.answer(t("export_failed", user.language))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
