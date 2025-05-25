import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planner_backend.settings")

import django

django.setup()

from aiogram import Bot, Dispatcher
from bot.logger import logger
from bot.handlers import (
    start,
    add_event,
    view_events,
    manage_events,
    export,
    import_csv,
    lang,
)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(add_event.router)
dp.include_router(view_events.router)
dp.include_router(manage_events.router)
dp.include_router(export.router)
dp.include_router(import_csv.router)
dp.include_router(lang.router)


async def main():
    print("MAIN STARTED ✅")
    logger.info("Bot started polling.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
