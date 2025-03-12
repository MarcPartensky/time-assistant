from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TIMEASSISTANT_")

    # Nextcloud parameters are mandatory
    nextcloud_user: str
    nextcloud_password: str
    nextcloud_board: str
    nextcloud_url: str

    app_name: str = "Time Assistant"
    debug: bool = False
    log_level: str = "Info"
    timezone: str = "Europe/Paris"
    zoneinfo: ZoneInfo = ZoneInfo(timezone)
    board_name: str = "-Todolist"
    deck_category: str = "Deck"

    personal_calendar: str = "Personal"
    work_calendar: str = "Taff"
    fitness_calendar: str = "Fitness"

    plan_day_limit: int = 1
    task_duration_hours: int = 2
    task_duration_minutes: int = 45

    work_start: int = 9
    work_end: int = 20
    lunch_start: int = 12
    lunch_end: int = 13
    dinner_start: int = 20
    dinner_end: int = 21

    @property
    def calendar_url(self):
        return f"{self.nextcloud_url}/remote.php/dav/calendars/{self.nextcloud_user}"


settings = Settings()

from pprint import pp

pp(settings)
