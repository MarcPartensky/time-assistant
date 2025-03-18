import caldav
import vobject

# from itertools import filter
# import itertools

from dateutil.rrule import rrule, DAILY, WEEKLY, MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import gettz
from datetime import datetime, timedelta
from ics import Calendar
from ics.alarm import DisplayAlarm
from typing import List, Optional, Dict, Iterator

# from ics.grammar.parse import ContentLine
# from collections import OrderedDict
# from nextcloud import NextCloud
# from app.services.logger import logger

from app.settings import settings
from app.models.smartevent import SmartEvent


client = settings.caldav_client
principal = client.principal()
calendars = principal.calendars()

today = datetime.today().date()
start_of_day = datetime.combine(today, datetime.min.time())  # 00:00:00
end_of_day = datetime.combine(today, datetime.max.time())  # 23:59:59

# nc = NextCloud(
#     endpoint=CALENDAR_URL, username=NEXTCLOUD_USER, password=NEXTCLOUD_PASSWORD
# )


def get_calendar(name: str) -> Optional[caldav.Calendar]:
    """Get calendar by name using list comprehension"""
    return next((c for c in settings.calendars if c.name == name), None)


# def modify_event(
#     event_uid: str,
#     new_event: SmartEvent,
#     calendar_name: str = settings.personal_calendar,
# ) -> bool:
#     """
#     Modifie un événement en utilisant un objet ics.Event
#     """
#     calendar = get_calendar(calendar_name)
#     if not calendar:
#         return False

#     # Récupérer l'événement existant
#     dav_event = calendar.event_by_uid(event_uid)
#     if not dav_event:
#         return False

#     # Convertir l'événement ics en vobject
#     # ics_cal = Calendar(events=[new_event])
#     vcal = ics_to_vobject(new_event)
#     vevent = vcal.vevent

#     vevent.uid.value = event_uid

#     data = vcal.serialize()
#     dav_event.data = data
#     dav_event.save()
#     return True


# def ics_to_vobject(ics_event: SmartEvent) -> vobject.base.Component:
#     """Convertit un événement ICS.py en VCALENDAR avec gestion des types"""
#     vcal = vobject.iCalendar()
#     vevent = vcal.add("vevent")

#     # Propriétés obligatoires avec conversion explicite
#     vevent.add("uid").value = str(ics_event.uid)
#     vevent.add("dtstamp").value = datetime.now(gettz("UTC"))
#     vevent.add("summary").value = str(ics_event.name)

#     vevent.add("dtstart").value = ics_event.begin.datetime
#     if ics_event.end:
#         vevent.add("dtend").value = ics_event.end.datetime

#     if ics_event.sequence:
#         vevent.add("sequence").value = str(ics_event.sequence)

#     if ics_event.description:
#         vevent.add("description").value = str(ics_event.description)

#     if ics_event.location:
#         vevent.add("location").value = str(ics_event.location)

#     if ics_event.categories:
#         # print("categories:")
#         # print(ics_event.categories)
#         # print(type(ics_event.categories))
#         # vevent.add("categories").value = ",".join(map(str, tuple(ics_event.categories)))
#         vevent.add("categories").value = ics_event.categories

#     if hasattr(ics_event, "status"):
#         if ics_event.status:
#             vevent.add("status").value = ics_event.status

#     if hasattr(ics_event, "transparent"):
#         vevent.add("transp").value = (
#             "TRANSPARENT" if ics_event.transparent else "OPAQUE"
#         )

#     return vcal

#     # # Géolocalisation avec formatage contrôlé
#     if hasattr(ics_event, "geo"):
#         if ics_event.geo:
#             if ics_event.geo.latitude and ics_event.geo.longitude:
#                 geo_value = f"{float(ics_event.geo.latitude):.6f};{float(ics_event.geo.longitude):.6f}"
#                 vevent.add("geo").value = geo_value

#     if hasattr(ics_event, "rrule"):
#         rrule_str = str(ics_event.rrule).replace("RRULE:", "")
#         vevent.add("rrule").value = rrule_str

#     if hasattr(ics_event, "exdates"):
#         if ics_event.exdates:
#             for exdate in ics_event.exdates:
#                 exdate_prop = vevent.add("exdate")
#                 exdate_prop.value = exdate.astimezone(gettz("UTC"))

#     # # Alarmes avec vérification de type
#     for alarm in ics_event.alarms:
#         valarm = vevent.add("valarm")
#         valarm.add("action").value = "DISPLAY"
#         valarm.add("trigger").value = alarm.trigger

#         if hasattr(alarm, "display_text"):
#             valarm.add("description").value = str(alarm.display_text)

#     extended_props = {
#         "url": "url",
#         "priority": "priority",
#         "class": "class",
#         "created": "created",
#         "last_modified": "last-modified",
#     }

#     for attr, prop in extended_props.items():
#         if hasattr(ics_event, attr):
#             value = getattr(ics_event, attr)
#             if isinstance(value, list):
#                 value = ",".join(map(str, value))
#             vevent.add(prop).value = str(value)

#     # Validation avant sauvegarde
#     if len(vevent.contents.get("dtstart", [])) > 1:
#         raise ValueError("Multiple DTSTART properties detected")

#     return vcal


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


def get_events_at(t: datetime) -> Iterator[SmartEvent]:
    for event in get_events():
        if event.begin < t < event.end:
            yield event


def get_focus_event_at(t: datetime) -> Optional[SmartEvent]:
    day = timedelta(days=1)
    coming_events = (
        e
        for e in get_events()
        if e.end >= t
        and (  # not a full day
            ((e.end - e.begin) % day).seconds != 0
            and e.begin == e.begin.replace(minute=0, second=0, microsecond=0)
        )
    )
    for e in sorted(coming_events, key=lambda e: (e.begin, e.end)):
        return e


def modify_description():
    events = get_events()
    if not events:
        return []

    # Convertir l'événement caldav en ics.Event
    # original_event = events[0]
    # event = SmartEvent(
    #     name="Nouveau nom d'événement",
    #     begin=original_event.begin.datetime,
    #     end=original_event.end.datetime,
    #     description="Nouvelle description",
    #     location="Nouveau lieu",
    #     # status=None,
    #     # status="CONFIRMED",
    #     alarms=[
    #         DisplayAlarm(trigger=timedelta(minutes=-15), display_text="allumer le feu"),
    #     ],
    # )

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

    event = events[0]
    # event.name = "Nouveau nom d'événement"
    event.description = "Nouvelle description"
    # event.location = "Nouveau lieu"
    # event.alarms=[
    #         DisplayAlarm(trigger=timedelta(minutes=-15), display_text="allumer le feu"),
    #     ],
    # )

    # Appliquer les modifications
    # success = modify_event(original_event.uid, event)
    # return {"success": success, "events": get_events()}
    return event.save_to_calendar("Personal")


def get_current_event_and_time_left():
    """Get the current and event and how much time is left to do the task."""
