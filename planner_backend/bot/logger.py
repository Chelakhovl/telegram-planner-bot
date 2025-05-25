import logging
from logging.handlers import RotatingFileHandler
import os

log_path = "logs/bot.log"
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s — %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
