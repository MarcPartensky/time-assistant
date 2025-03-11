import os
from dotenv import load_dotenv

load_dotenv()

NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
NEXTCLOUD_USER = os.getenv("NEXTCLOUD_USER")
NEXTCLOUD_PASSWORD = os.getenv("NEXTCLOUD_PASSWORD")
NEXTCLOUD_BOARD = os.getenv("NEXTCLOUD_BOARD")

if not all([NEXTCLOUD_URL, NEXTCLOUD_USER, NEXTCLOUD_PASSWORD, NEXTCLOUD_BOARD]):
    raise Exception("Missing required environment variables.")

TIMEZONE = os.getenv("TIMEZONE") or "Europe/Paris"
