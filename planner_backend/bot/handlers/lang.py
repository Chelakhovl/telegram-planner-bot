from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from user.services import get_or_create_user
from bot.locale.utils import t
from asgiref.sync import sync_to_async
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("language"))
async def change_language(message: Message):
    """
    Toggle user language between 'ua' and 'en'.
    """
    user = await get_or_create_user(message.from_user.id)

    if user.language == "ua":
        user.language = "en"
    else:
        user.language = "ua"

    await sync_to_async(user.save)()

    await message.answer(t("language_changed", user.language))
    logger.info(f"Language changed to {user.language} for user {user.telegram_id}")
