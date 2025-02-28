import caldav
import vobject

from dateutil.rrule import rrule, DAILY, WEEKLY, MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import gettz
from datetime import datetime, timedelta
from ics import Calendar, Event
from ics.alarm import DisplayAlarm
from ics.grammar.parse import ContentLine

from collections import OrderedDict
from typing import List, Optional, Dict

from nextcloud import NextCloud

# import requests

# from app.services.logger import logger
from app.env import *

CALENDAR_NAME = "Personal"

# Connect to Nextcloud CalDAV server
CALENDAR_URL = f"{NEXTCLOUD_URL}/remote.php/dav/calendars/{NEXTCLOUD_USER}"
print(CALENDAR_URL)

client = caldav.DAVClient(
    CALENDAR_URL, username=NEXTCLOUD_USER, password=NEXTCLOUD_PASSWORD
)
# client.calendar
# print(client.calendar(CALENDAR_URL + "/Personal"))
principal = client.principal()
print(principal)
calendars = principal.calendars()
today = datetime.today().date()
start_of_day = datetime.combine(today, datetime.min.time())  # 00:00:00
end_of_day = datetime.combine(today, datetime.max.time())  # 23:59:59
# calendards = client.calendar


class SmartEvent(Event):
    def __init__(self, *args, rrule=None, **kwargs):
        """
        rrule_obj : un objet dateutil.rrule (optionnel).
        """
        super().__init__(*args, **kwargs)
        if rrule is not None:
            self.rrule = convert_rrule_to_str(rrule)

    @property
    def rrule_obj(self):
        # Pour simplifier, on retourne la chaîne RRULE actuelle
        return self.rrule

    @rrule_obj.setter
    def rrule_obj(self, rule):
        self.rrule = convert_rrule_to_str(rule)


# response = requests.get(CALENDAR_URL, auth=(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD))
# calendar = Calendar(response.text)

# for calendar in calendars:
#     events = calendar.date_search(today, today)
#     for event in events:
#         print(f"Event: {event.instance.vevent.summary}")
#         print(f"Start: {event.instance.vevent.dtstart}")
#         print(f"End: {event.instance.vevent.dtend}")


# nc = NextCloud(
#     endpoint=CALENDAR_URL, username=NEXTCLOUD_USER, password=NEXTCLOUD_PASSWORD
# )


# def get_events() -> List[OrderedDict]:
#     event_list = []
#     # start=datetime(2021, 1, 1), end=datetime(2024, 1, 1),event=True, expand=True)
#     for calendar in calendars:
#         events = calendar.date_search(start_of_day, end_of_day)
#         for event in events:
#             # instance = event.instance
#             vevent: Event = event.instance.vevent
#             # vevent.start
#             start = vevent.dtstart.value
#             end = vevent.dtend.value
#             summary = vevent.summary
#             # print(summary)
#             properties = event.get_properties()
#             # event.url
#             # last_modified = properties["{DAV:}getlastmodified"]
#             # print(last_modified)
#             # print(event.get_properties())
#             # event.instance.validate
#             url = event.canonical_url
#             # url = event.url["url_raw"],

#             event_data = OrderedDict(
#                 name=summary.value,
#                 url=url,
#                 duration=event.get_duration(),
#                 # description=vevent.description,
#                 start=start,
#                 end=end,
#                 # instance=instance,
#                 # vevent=vevent.location,
#             )
#             # print(summary)
#             event_list.append(event_data)
#             break

#             # print(event_list)
#     return event_list


# def get_events2() -> List[OrderedDict]:
#     event_list = []

#     # CALENDAR_URL = f"{NEXTCLOUD_URL}/remote.php/dav/calendars/{NEXTCLOUD_USER}"
#     calendar_path = CALENDAR_URL + "/Personal"

#     # calendar_path = f'/remote.php/dav/calendars/{username}/{calendar_name}'
#     # print(calendar_path)
#     # print(calendars[0].name)
#     personal_calendar = calendars[0]
#     print("calendar name:", personal_calendar.name)

#     events = personal_calendar.date_search(start_of_day, end_of_day)
#     event = events[0]
#     print("events number:", len(events))

#     for event in events:
#         # print(event.description)
#         print("event data:", event.data)
#         print("dtend:", event.get_dtend())
#         # print("children:", event.children())
#         print("wire data:", event.wire_data)
#         print("vobject instance:", event.vobject_instance.serialize())
#         # properties = event.get_properties("{DAV:}getetag")
#         # print(properties)
#         # properties: dict = event.get_properties()
#         # print(type(properties))
#         # print("properties:", event.get_properties())
#         # print("etag:", properties["{DAV:}getetag"])
#         # print(event.get_duration())
#         # instance = event.instance
#         vevent: Event = event.instance.vevent
#         start = vevent.dtstart.value
#         end = vevent.dtend.value

#         summary = vevent.summary
#         print(vevent.__dict__)
#         properties = event.get_properties()
#         # event.url
#         # last_modified = properties["{DAV:}getlastmodified"]
#         # print(last_modified)

#         event_data = OrderedDict(
#             name=summary.value,
#             url=event.canonical_url,
#             duration=event.get_duration(),
#             start=vevent.dtstart.value,
#             end=vevent.dtend.value,
#             location=vevent.contents["location"],
#             description=vevent.get("description"),
#             recurrence=vevent.get("rrule"),
#             duedate=event.get_due(),
#             wire_data=event.wire_data,
#         )

#         # Récupérer le contenu du calendrier
#         # calendar_content = nc.download_file(calendar_path)

#         # # Parser le calendrier avec icalendar
#         # from icalendar import Calendar

#         # calendar = Calendar.from_ical(calendar_content)

#         # print("https://cloud.marcpartensky.com/remote.php/dav/calendars/marc")
#         # calendar_url = "https://cloud.marcpartensky.com/remote.php/dav/calendars/marc"
#         # print(calendar_url)
#         # headers = {"Accept": "text/calendar"}
#         # response = requests.get(
#         #     calendar_url,
#         #     auth=(str(NEXTCLOUD_USER), str(NEXTCLOUD_PASSWORD)),
#         #     headers=headers,
#         # )
#         # print(response)

#         # calendar = Calendar(response.text)

#         # calendar = Calendar.from_ical(response.text)
#         # for component in calendar.walk():
#         #     if component.name == "VEVENT":
#         #         event_list.append(
#         #             {
#         #                 "summary": component.get("summary"),
#         #                 "start": component.get("dtstart").dt,
#         #                 "end": component.get("dtend").dt,
#         #                 # Ajouter d'autres propriétés selon vos besoins
#         #             }
#         #         )

#         event_list.append(event_data)
#     return event_list


# def get_events3():
#     event_list = []
#     print(calendars)
#     personal_calendar = calendars[1]
#     print(personal_calendar)
#     for calendar in calendars:
#         events = personal_calendar.date_search(start_of_day, end_of_day)
#         print(len(events), "events found")

#         for event in events:
#             # Récupérer la chaîne ICS de l'événement
#             raw_ics = event.data  # ou event.vobject_instance.serialize()

#             # Parser l'ICS avec ICS.py
#             cal = Calendar(raw_ics)
#             # On suppose qu'il n'y a qu'un événement dans le fichier ICS
#             ev = list(cal.events)[0]

#             # Modifier les propriétés via l'API ICS.py
#             print(ev)
#             # ev.name = "Nouveau titre"             # équivalent à SUMMARY
#             # ev.location = "Nouvelle location"
#             ev.description = "Nouvelle description"
#             print("new:", ev)

#             # Pour la récurrence, ICS.py permet de définir une règle (attention : support limité)
#             # Par exemple, pour un événement quotidien :
#             # ev.extra = [("rrule", "FREQ=DAILY;INTERVAL=1")]

#             # Re-sérialiser le calendrier en ICS
#             new_ics = cal.serialize()
#             print(new_ics)

#             # Mettre à jour l'événement sur le serveur distant
#             ical_event = event.icalendar_instance
#             event.set_properties({"SUMMARY": "osef"})
#             print("ical event:", ical_event)
#             ical_event["SUMMARY"] = "Nouveau résumé de l'événement"
#             event.data = ical_event.to_ical()
#             print("event.data:", event.data)
#             event.save()
#             ical_event = event.icalendar_instance
#             print("ical event:", ical_event)
#             event_list.append(event)

#     return event_list


# def build_rrule(freq, interval=1, until=None, count=None, byday=None):
#     """
#     Construit une chaîne RRULE conforme à RFC5545.

#     :param freq: Fréquence (ex: "DAILY", "WEEKLY", etc.)
#     :param interval: Intervalle entre chaque occurrence (entier)
#     :param until: Date de fin (datetime)
#     :param count: Nombre d'occurrences (entier)
#     :param byday: Liste de jours (ex: ["MO", "WE", "FR"])
#     :return: Chaîne RRULE
#     """
#     parts = []
#     parts.append("FREQ=" + freq)
#     parts.append("INTERVAL=" + str(interval))
#     if until:
#         # Format attendu : AAAAMMJJTHHMMSSZ (UTC)
#         parts.append("UNTIL=" + until.strftime("%Y%m%dT%H%M%SZ"))
#     if count:
#         parts.append("COUNT=" + str(count))
#     if byday:
#         parts.append("BYDAY=" + ",".join(byday))
#     return ";".join(parts)


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
    event_uid: str, new_event: SmartEvent, calendar_name: str = CALENDAR_NAME
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

    # Gestion de DTSTAMP
    if not hasattr(vevent, "dtstamp"):
        vevent.add("dtstamp")
    vevent.dtstamp.value = datetime.now(gettz("UTC"))

    # Mettre à jour la séquence
    if hasattr(vevent, "sequence"):
        vevent.sequence.value += 1
    else:
        vevent.add("sequence").value = 1
    vevent.sequence.value = str(vevent.sequence.value)

    # Validation avant sauvegarde
    if len(vevent.contents.get("dtstart", [])) > 1:
        raise ValueError("Multiple DTSTART properties detected")

    data = vcal.serialize()
    print(data)
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

    # Conversion numérique en chaîne pour SEQUENCE
    vevent.add("sequence").value = 0

    # Gestion des dates
    vevent.add("dtstart").value = ics_event.begin.datetime
    if ics_event.end:
        vevent.add("dtend").value = ics_event.end.datetime

    # Propriétés textuelles
    vevent.add("summary").value = str(ics_event.name)
    if ics_event.description:
        vevent.add("description").value = str(ics_event.description)
    if ics_event.location:
        vevent.add("location").value = str(ics_event.location)

    # Récurrence avec conversion forcée
    if hasattr(ics_event, "rrule"):
        rrule_str = str(ics_event.rrule).replace("RRULE:", "")
        vevent.add("rrule").value = rrule_str

    # Exceptions (EXDATE)
    if hasattr(ics_event, "exdates"):
        for exdate in ics_event.exdates:
            exdate_prop = vevent.add("exdate")
            exdate_prop.value = exdate.astimezone(gettz("UTC"))

    # Statut et transparence
    if hasattr(ics_event, "status"):
        if ics_event.status:
            vevent.add("status").value = ics_event.status

    if hasattr(ics_event, "transparency"):
        vevent.add("transp").value = (
            "TRANSPARENT" if ics_event.transparency else "OPAQUE"
        )

    # Alarmes avec vérification de type
    for alarm in ics_event.alarms:
        valarm = vevent.add("valarm")
        valarm.add("action").value = "DISPLAY"
        valarm.add("trigger").value = alarm.trigger

        if hasattr(alarm, "display_text"):
            valarm.add("description").value = str(alarm.display_text)

    # Géolocalisation avec formatage contrôlé
    if hasattr(ics_event, "latitude") and hasattr(ics_event, "longitude"):
        geo_value = f"{float(ics_event.latitude):.6f};{float(ics_event.longitude):.6f}"
        vevent.add("geo").value = geo_value

    # Catégories formatées
    if ics_event.categories:
        vevent.add("categories").value = ",".join(map(str, ics_event.categories))

    extended_props = {
        # "url": "url",
        # "priority": "priority",
        # "categories": "categories",
        # "class": "class",
        # "created": "created",
        # "last_modified": "last-modified",
    }

    for attr, prop in extended_props.items():
        if hasattr(ics_event, attr):
            value = getattr(ics_event, attr)
            if isinstance(value, list):
                value = ",".join(map(str, value))
            vevent.add(prop).value = str(value)

    return vcal


def get_events(
    start: datetime = start_of_day,
    end: datetime = end_of_day,
    calendar_name: str = CALENDAR_NAME,
) -> list[SmartEvent]:
    """Get events using ICS.py for parsing"""
    if not (calendar := get_calendar(calendar_name)):
        return []

    try:
        events = calendar.date_search(start, end)
        # Convert the set to a list before accessing elements
        return [next(iter(Calendar(e.data).events)) for e in events]
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []


def modify_description():
    events = get_events()
    if not events:
        return []

    # Convertir l'événement caldav en ics.Event
    original_event = events[0]
    event = Event(
        name="Nouveau nom d'événement",
        begin=original_event.begin.datetime,
        end=original_event.end.datetime,
        description="Nouvelle description",
        location="Nouveau lieu",
        # status="CONFIRMED",
        alarms=[
            DisplayAlarm(trigger=timedelta(minutes=-15), display_text="allumer le feu"),
        ],
    )
    print("status:", event.status)
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


if __name__ == "__main__":
    print(principal)
