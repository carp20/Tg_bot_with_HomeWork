import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
OWNER_ID = int(os.getenv("OWNER_ID", 0))


PROJECT_STATUSES = ["Owner", "Admin", "Staff", "Member"]
TEAM_ROLES = ["староста", "помощник старосты", "участник"]