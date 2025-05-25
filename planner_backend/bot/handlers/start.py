from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from user.services import get_or_create_user
from bot.locale.utils import t

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    user = await get_or_create_user(message.from_user.id)
    await message.answer(t("start", user.language))
