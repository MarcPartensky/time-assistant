import caldav
import vobject

from dateutil.rrule import rrule, DAILY, WEEKLY, MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import gettz
from datetime import datetime, timedelta
from ics import Calendar, Event
from ics.alarm import DisplayAlarm
from typing import List, Optional, Dict

# from ics.grammar.parse import ContentLine
# from collections import OrderedDict
# from nextcloud import NextCloud
# from app.services.logger import logger

from app.settings import settings


client = caldav.DAVClient(
    settings.calendar_url,
    username=settings.nextcloud_user,
    password=settings.nextcloud_password,
)

principal = client.principal()
calendars = principal.calendars()

today = datetime.today().date()
start_of_day = datetime.combine(today, datetime.min.time())  # 00:00:00
end_of_day = datetime.combine(today, datetime.max.time())  # 23:59:59

# nc = NextCloud(
#     endpoint=CALENDAR_URL, username=NEXTCLOUD_USER, password=NEXTCLOUD_PASSWORD
# )


class SmartEvent(Event):
    def __init__(
        self,
        *args,
        rrule=None,
        exdates=None,
        sequence=None,
        **kwargs,
    ):
        """
        rrule_obj : un objet dateutil.rrule (optionnel).
        """
        super().__init__(*args, **kwargs)
        if rrule is not None:
            self._rrule = rrule
        self.exdates = exdates
        self.sequence = sequence

    @classmethod
    def from_icsevent(cls, event: Event):
        return cls(
            uid=event.uid,
            created=event.created,
            last_modified=event.last_modified,
            name=event.name,
            begin=event.begin,
            end=event.end,
            # duration=event.duration,
            # all_day=event.all_day,
            description=event.description,
            location=event.location,
            url=event.url,
            status=event.status,
            classification=event.classification,
            organizer=event.organizer,
            attendees=event.attendees,
            alarms=event.alarms,
            categories=event.categories,
        )

    @property
    def rrule(self):
        # Pour simplifier, on retourne la chaîne RRULE actuelle
        return convert_rrule_to_str(self._rrule)

    def set_rrule(self, rrule):
        self._rrule = rrule

    def save_to_calendar(self, calendar_name: str):
        """Sauvegarde dans un calendrier"""
        calendar = get_calendar(calendar_name)
        if not calendar:
            return False

        vcal = ics_to_vobject(self)
        data = vcal.serialize()
        calendar.add_event(data)
        return True

    def __str__(self):
        t = "SmartEvent("
        t += self.begin.strftime("%Y-%m-%d %H:%M") + ", "
        t += self.end.strftime("%Y-%m-%d %H:%M") + ", "
        t += self.name
        t += ")"
        return t


def convert_rrule_to_str(rule):
    """
    Convertit un objet dateutil.rrule en chaîne conforme à RFC5545.
    Attention : ici on utilise des attributs internes de l'objet rrule.
    """
    freq_map = {
        0: "SECONDLY",
        1: "MINUTELY",
        2: "HOURLY",
        3: "DAILY",
        4: "WEEKLY",
        5: "MONTHLY",
        6: "YEARLY",
    }
    parts = []
    freq = rule._freq
    parts.append("FREQ=" + freq_map.get(freq, "DAILY"))

    if rule._interval != 1:
        parts.append("INTERVAL=" + str(rule._interval))

    if rule._until:
        parts.append("UNTIL=" + rule._until.strftime("%Y%m%dT%H%M%SZ"))

    if rule._count:
        parts.append("COUNT=" + str(rule._count))

    if rule._byweekday:
        day_map = {0: "MO", 1: "TU", 2: "WE", 3: "TH", 4: "FR", 5: "SA", 6: "SU"}
        weekdays = []
        for wd in rule._byweekday:
            weekdays.append(day_map.get(wd.weekday, "MO"))
        parts.append("BYDAY=" + ",".join(weekdays))

    return ";".join(parts)


def get_calendar(name: str) -> Optional[caldav.Calendar]:
    """Get calendar by name using list comprehension"""
    return next((c for c in client.principal().calendars() if c.name == name), None)


def modify_event(
    event_uid: str,
    new_event: SmartEvent,
    calendar_name: str = settings.personal_calendar,
) -> bool:
    """
    Modifie un événement en utilisant un objet ics.Event
    """
    calendar = get_calendar(calendar_name)
    if not calendar:
        return False

    # Récupérer l'événement existant
    dav_event = calendar.event_by_uid(event_uid)
    if not dav_event:
        return False

    # Convertir l'événement ics en vobject
    # ics_cal = Calendar(events=[new_event])
    vcal = ics_to_vobject(new_event)
    vevent = vcal.vevent

    vevent.uid.value = event_uid

    data = vcal.serialize()
    dav_event.data = data
    dav_event.save()
    return True


def ics_to_vobject(ics_event: SmartEvent) -> vobject.base.Component:
    """Convertit un événement ICS.py en VCALENDAR avec gestion des types"""
    vcal = vobject.iCalendar()
    vevent = vcal.add("vevent")

    # Propriétés obligatoires avec conversion explicite
    vevent.add("uid").value = str(ics_event.uid)
    vevent.add("dtstamp").value = datetime.now(gettz("UTC"))
    vevent.add("summary").value = str(ics_event.name)

    vevent.add("dtstart").value = ics_event.begin.datetime
    if ics_event.end:
        vevent.add("dtend").value = ics_event.end.datetime

    if ics_event.sequence:
        vevent.add("sequence").value = str(ics_event.sequence)

    if ics_event.description:
        vevent.add("description").value = str(ics_event.description)

    if ics_event.location:
        vevent.add("location").value = str(ics_event.location)

    if ics_event.categories:
        # print("categories:")
        # print(ics_event.categories)
        # print(type(ics_event.categories))
        # vevent.add("categories").value = ",".join(map(str, tuple(ics_event.categories)))
        vevent.add("categories").value = ics_event.categories

    if hasattr(ics_event, "status"):
        if ics_event.status:
            vevent.add("status").value = ics_event.status

    if hasattr(ics_event, "transparent"):
        vevent.add("transp").value = (
            "TRANSPARENT" if ics_event.transparent else "OPAQUE"
        )

    return vcal

    # # Géolocalisation avec formatage contrôlé
    if hasattr(ics_event, "geo"):
        if ics_event.geo:
            if ics_event.geo.latitude and ics_event.geo.longitude:
                geo_value = f"{float(ics_event.geo.latitude):.6f};{float(ics_event.geo.longitude):.6f}"
                vevent.add("geo").value = geo_value

    if hasattr(ics_event, "rrule"):
        rrule_str = str(ics_event.rrule).replace("RRULE:", "")
        vevent.add("rrule").value = rrule_str

    if hasattr(ics_event, "exdates"):
        if ics_event.exdates:
            for exdate in ics_event.exdates:
                exdate_prop = vevent.add("exdate")
                exdate_prop.value = exdate.astimezone(gettz("UTC"))

    # # Alarmes avec vérification de type
    for alarm in ics_event.alarms:
        valarm = vevent.add("valarm")
        valarm.add("action").value = "DISPLAY"
        valarm.add("trigger").value = alarm.trigger

        if hasattr(alarm, "display_text"):
            valarm.add("description").value = str(alarm.display_text)

    extended_props = {
        "url": "url",
        "priority": "priority",
        "class": "class",
        "created": "created",
        "last_modified": "last-modified",
    }

    for attr, prop in extended_props.items():
        if hasattr(ics_event, attr):
            value = getattr(ics_event, attr)
            if isinstance(value, list):
                value = ",".join(map(str, value))
            vevent.add(prop).value = str(value)

    # Validation avant sauvegarde
    if len(vevent.contents.get("dtstart", [])) > 1:
        raise ValueError("Multiple DTSTART properties detected")

    return vcal


def get_events(
    # calendar_name: str = PERSONAL_CALENDAR,
    start: datetime = start_of_day,
    end: datetime = end_of_day,
) -> list[SmartEvent]:
    """Get events using ICS.py for parsing"""
    caldav_events = []
    for calendar in calendars:
        caldav_events.extend(calendar.date_search(start, end))
    events = [
        SmartEvent.from_icsevent(next(iter(Calendar(e.data).events)))
        for e in caldav_events
    ]
    events.sort(key=lambda x: x.begin)
    return events


def modify_description():
    events = get_events()
    if not events:
        return []

    # Convertir l'événement caldav en ics.Event
    original_event = events[0]
    event = SmartEvent(
        name="Nouveau nom d'événement",
        begin=original_event.begin.datetime,
        end=original_event.end.datetime,
        description="Nouvelle description",
        location="Nouveau lieu",
        # status=None,
        # status="CONFIRMED",
        alarms=[
            DisplayAlarm(trigger=timedelta(minutes=-15), display_text="allumer le feu"),
        ],
    )
    # event.rrule = convert_rrule_to_str(
    #     rrule(
    #         freq=DAILY,
    #         interval=1,
    #         until=datetime(2025, 12, 31, 23, 59, 59),
    #         byweekday=(MO, WE),
    #     )
    # )
    # event = SmartEvent(**event.__dict__)
    # print(event.rrule)

    # Ajouter une récurrence
    # ics_event.rrule = {
    #     "freq": "WEEKLY",
    #     "interval": 2,
    #     "byday": ["MO", "WE"],
    #     "until": datetime(2025, 3, 31, 21, 0, tzinfo=gettz("UTC")),
    # }

    # Appliquer les modifications
    success = modify_event(original_event.uid, event)
    return {"success": success, "events": get_events()}


def get_current_event_and_time_left():
    """Get the current and event and how much time is left to do the task."""


if __name__ == "__main__":
    print(principal)
