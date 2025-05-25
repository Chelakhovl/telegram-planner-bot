import os
import datetime
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backup_dir = os.path.join(BASE_DIR, "backups")
os.makedirs(backup_dir, exist_ok=True)
backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.sql")


command = [
    "pg_dump",
    "-h",
    DB_HOST,
    "-p",
    DB_PORT,
    "-U",
    DB_USER,
    "-F",
    "p",
    "-d",
    DB_NAME,
    "-f",
    backup_file,
]

env = os.environ.copy()
env["PGPASSWORD"] = DB_PASSWORD

try:
    subprocess.run(command, env=env, check=True)
    logger.info(f"Backup created: {backup_file}")
except subprocess.CalledProcessError as e:
    logger.error(f"Backup failed: {e}")
