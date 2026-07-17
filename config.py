import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PREFIX = os.getenv("BOT_PREFIX", "!")
BOT_STATUS = os.getenv("BOT_STATUS", "Playing with commands | !help")
EMBED_COLOR = 0x5865F2
ERROR_COLOR = 0xED4245
SUCCESS_COLOR = 0x57F287
WARNING_COLOR = 0xFEE75C
INFO_COLOR = 0x5865F2
DATABASE_PATH = "database.db"
