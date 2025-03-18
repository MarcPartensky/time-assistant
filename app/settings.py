from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import caldav

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
    board_name: str = "-Todolist"
    deck_category: str = "Deck"

    personal_calendar: str = "Personal"
    work_calendar: str = "Taff"
    fitness_calendar: str = "Fitness"

    plan_day_limit: int = 1
    task_duration_hours: int = 3
    task_duration_minutes: int = 0

    work_start: int = 9
    work_end: int = 20
    lunch_start: int = 12
    lunch_end: int = 13
    dinner_start: int = 20
    dinner_end: int = 21

    api_key: str = "osef"

    @property
    def zoneinfo(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @property
    def calendar_url(self):
        return f"{self.nextcloud_url}/remote.php/dav/calendars/{self.nextcloud_user}"

    @property
    def caldav_client(self) -> caldav.DAVClient:
        """Return caldav client"""
        return caldav.DAVClient(
            self.calendar_url,
            username=self.nextcloud_user,
            password=self.nextcloud_password,
        )

    @property
    def principal(self) -> caldav.Principal:
        """Return principal"""
        return self.caldav_client.principal()

    @property
    def calendars(self) -> List[caldav.Calendar]:
        """Return calendars"""
        return self.principal.calendars()


settings = Settings()

from pprint import pp

pp(settings)
