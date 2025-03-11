from dotenv import load_dotenv

load_dotenv()

# NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
# NEXTCLOUD_USER = os.getenv("NEXTCLOUD_USER")
# NEXTCLOUD_PASSWORD = os.getenv("NEXTCLOUD_PASSWORD")
# NEXTCLOUD_BOARD = os.getenv("NEXTCLOUD_BOARD")

# if not all([NEXTCLOUD_URL, NEXTCLOUD_USER, NEXTCLOUD_PASSWORD, NEXTCLOUD_BOARD]):
#     raise Exception("Missing required environment variables.")

# TIMEZONE = os.getenv("TIMEZONE") or "Europe/Paris"


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Time Assistant"
    debug: bool = False
    log_level: str = "Info"
    timezone: str = "Europe/Paris"
    board_name: str = "-Todolist"
    calendar_name: str = "Personal"

    nextcloud_user: str
    nextcloud_password: str
    nextcloud_board: str
    nextcloud_url: str

    @property
    def calendar_url(self):
        return f"{self.nextcloud_url}/remote.php/dav/calendars/{self.nextcloud_user}"

    # Vous pouvez définir un préfixe pour vos variables d'environnement
    model_config = SettingsConfigDict(env_prefix="TIMEASSISTANT_")


settings = Settings()

from pprint import pp

pp(settings)
