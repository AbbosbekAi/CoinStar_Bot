import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")

# SMM panel API sozlamalari (agar DB'da bo'lmasa shu yerdan olinadi)
SMM_API_URL = os.getenv("SMM_API_URL", "")
SMM_API_KEY = os.getenv("SMM_API_KEY", "")
SMM_MARGIN_PERCENT = float(os.getenv("SMM_MARGIN_PERCENT", "25"))

DAILY_BONUS_AMOUNT = int(os.getenv("DAILY_BONUS_AMOUNT", "100"))
REFERRAL_BONUS_AMOUNT = int(os.getenv("REFERRAL_BONUS_AMOUNT", "500"))
MIN_WITHDRAW = int(os.getenv("MIN_WITHDRAW", "1000"))