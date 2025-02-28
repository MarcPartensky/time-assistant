import caldav

from dateutil.tz import gettz
import vobject

from datetime import datetime, timedelta
from ics import Calendar, Event

from collections import OrderedDict
from typing import List, Optional, Dict, Union

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

# response = requests.get(CALENDAR_URL, auth=(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD))
# calendar = Calendar(response.text)

# for calendar in calendars:
#     events = calendar.date_search(today, today)
#     for event in events:
#         print(f"Event: {event.instance.vevent.summary}")
#         print(f"Start: {event.instance.vevent.dtstart}")
#         print(f"End: {event.instance.vevent.dtend}")


nc = NextCloud(
    endpoint=CALENDAR_URL, username=NEXTCLOUD_USER, password=NEXTCLOUD_PASSWORD
)


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


def get_calendar(name: str) -> Optional[caldav.Calendar]:
    """Get calendar by name using list comprehension"""
    return next((c for c in client.principal().calendars() if c.name == name), None)


def get_events2() -> List[OrderedDict]:
    event_list = []

    # CALENDAR_URL = f"{NEXTCLOUD_URL}/remote.php/dav/calendars/{NEXTCLOUD_USER}"
    calendar_path = CALENDAR_URL + "/Personal"

    # calendar_path = f'/remote.php/dav/calendars/{username}/{calendar_name}'
    # print(calendar_path)
    # print(calendars[0].name)
    personal_calendar = calendars[0]
    print("calendar name:", personal_calendar.name)

    events = personal_calendar.date_search(start_of_day, end_of_day)
    event = events[0]
    print("events number:", len(events))

    for event in events:
        # print(event.description)
        print("event data:", event.data)
        print("dtend:", event.get_dtend())
        # print("children:", event.children())
        print("wire data:", event.wire_data)
        print("vobject instance:", event.vobject_instance.serialize())
        # properties = event.get_properties("{DAV:}getetag")
        # print(properties)
        # properties: dict = event.get_properties()
        # print(type(properties))
        # print("properties:", event.get_properties())
        # print("etag:", properties["{DAV:}getetag"])
        # print(event.get_duration())
        # instance = event.instance
        vevent: Event = event.instance.vevent
        start = vevent.dtstart.value
        end = vevent.dtend.value

        summary = vevent.summary
        print(vevent.__dict__)
        properties = event.get_properties()
        # event.url
        # last_modified = properties["{DAV:}getlastmodified"]
        # print(last_modified)

        event_data = OrderedDict(
            name=summary.value,
            url=event.canonical_url,
            duration=event.get_duration(),
            start=vevent.dtstart.value,
            end=vevent.dtend.value,
            location=vevent.contents["location"],
            description=vevent.get("description"),
            recurrence=vevent.get("rrule"),
            duedate=event.get_due(),
            wire_data=event.wire_data,
        )

        # Récupérer le contenu du calendrier
        # calendar_content = nc.download_file(calendar_path)

        # # Parser le calendrier avec icalendar
        # from icalendar import Calendar

        # calendar = Calendar.from_ical(calendar_content)

        # print("https://cloud.marcpartensky.com/remote.php/dav/calendars/marc")
        # calendar_url = "https://cloud.marcpartensky.com/remote.php/dav/calendars/marc"
        # print(calendar_url)
        # headers = {"Accept": "text/calendar"}
        # response = requests.get(
        #     calendar_url,
        #     auth=(str(NEXTCLOUD_USER), str(NEXTCLOUD_PASSWORD)),
        #     headers=headers,
        # )
        # print(response)

        # calendar = Calendar(response.text)

        # calendar = Calendar.from_ical(response.text)
        # for component in calendar.walk():
        #     if component.name == "VEVENT":
        #         event_list.append(
        #             {
        #                 "summary": component.get("summary"),
        #                 "start": component.get("dtstart").dt,
        #                 "end": component.get("dtend").dt,
        #                 # Ajouter d'autres propriétés selon vos besoins
        #             }
        #         )

        event_list.append(event_data)
    return event_list


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


def modify_event(
    event_uid: str, changes: Dict, calendar_name: str = CALENDAR_NAME
) -> bool:
    """
    Modifie un événement avec gestion des propriétés existantes
    """
    calendar = get_calendar(calendar_name)
    if not calendar:
        return False

    dav_event = calendar.event_by_uid(event_uid)
    if not dav_event:
        return False

    vcal = dav_event.vobject_instance
    vevent = vcal.vevent

    # Gestion des propriétés existantes
    def update_property(prop_name, value):
        if prop_name in vevent.contents:
            vevent.contents[prop_name][0].value = value
        else:
            vevent.add(prop_name).value = value

    # Mise à jour DTSTAMP
    update_property("dtstamp", datetime.now(gettz("UTC")))

    # Gestion des propriétés simples
    property_mapping = {
        "summary": "summary",
        "location": "location",
        "description": "description",
        "url": "url",
        "priority": "priority",
        "categories": "categories",
    }

    for key, prop in property_mapping.items():
        if key in changes:
            value = changes[key]
            if value is None:
                if prop in vevent.contents:
                    del vevent.contents[prop]
            else:
                update_property(prop, value)

    # Gestion des dates (DTSTART/DTEND)
    time_props = {"start": "dtstart", "end": "dtend", "due": "due"}

    for key, prop in time_props.items():
        if key in changes:
            if prop in vevent.contents:
                vevent.contents[prop][0].value = changes[key]
            else:
                vevent.add(prop).value = changes[key]

    # Récurrence
    if "rrule" in changes:
        _handle_rrule(vevent, changes["rrule"])

    if "exdates" in changes:
        _handle_exdates(vevent, changes["exdates"])

    # Alarmes
    if "alarms" in changes:
        _handle_alarms(vevent, changes["alarms"])

    # Géolocalisation
    if "geo" in changes:
        vevent.add("geo").value = changes["geo"]

    # Statut
    if "status" in changes:
        vevent.add("status").value = changes["status"].upper()

    # Transparence
    if "transparency" in changes:
        vevent.add("transp").value = changes["transparency"].upper()

    # Validation avant sauvegarde
    if len(vevent.contents.get("dtstart", [])) > 1:
        raise ValueError("Multiple DTSTART properties detected")

    dav_event.data = vcal.serialize()
    dav_event.save()
    return True


def _handle_exdates(vevent, exdates: List[datetime]):
    """Gère les dates d'exclusion"""
    if hasattr(vevent, "exdate"):
        del vevent.exdate

    for exdate in exdates:
        exdate_prop = vevent.add("exdate")
        exdate_prop.value = exdate


def _handle_rrule(vevent, rrule: Union[str, dict]):
    """Gestion corrigée des règles de récurrence"""
    if isinstance(rrule, dict):
        # Conversion en chaîne RRULE valide
        parts = []
        for key, value in rrule.items():
            key = key.upper()  # Les clés doivent être en majuscules
            if isinstance(value, list):
                value = ",".join(value)
            parts.append(f"{key}={value}")
        rrule_str = ";".join(parts)
    else:
        rrule_str = rrule

    # Mise à jour ou ajout de la règle
    if hasattr(vevent, "rrule"):
        vevent.rrule.value = rrule_str
    else:
        vevent.add("rrule").value = rrule_str


def _handle_alarms(vevent, alarms: List[dict]):
    """Gestion corrigée des alarmes"""
    # Correction de la suppression des anciennes alarmes
    for component in list(vevent.components()):  # Conversion en liste
        if component.name == "VALARM":
            vevent.remove(component)

    # Ajout des nouvelles alarmes
    for alarm in alarms:
        valarm = vevent.add("valarm")
        valarm.add("action").value = alarm.get("action", "DISPLAY").upper()

        trigger = alarm.get("trigger")
        trigger_prop = valarm.add("trigger")

        if isinstance(trigger, datetime):
            trigger_prop.value = trigger
        else:
            # Format relatif avec paramètre RELATED
            trigger_prop.value = trigger
            if isinstance(trigger, str) and trigger.startswith("-"):
                trigger_prop.params["RELATED"] = ["START"]

        if "description" in alarm:
            valarm.add("description").value = alarm["description"]


def get_events(
    start: datetime = datetime.today(),
    end: datetime = datetime.today() + timedelta(days=1),
    calendar_name: str = CALENDAR_NAME,
) -> list[Event]:
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
    event = events[0]
    # modify_event(
    #     event.uid,
    #     {
    #         "name": "musée de la noche",
    #         "description": "ca va etre la fiesta",
    #     },
    # )

    changes = {
        "summary": "musée de la noche",
        "description": "ca va etre la fiesta",
        "location": "Le louvre",
        "rrule": {
            "FREQ": "DAILY",
            # "INTERVAL": 1,
            "BYDAY": ["MO", "WE"],
            "UNTIL": "20250331T210000Z",
        },
        "alarms": [
            {
                "action": "DISPLAY",
                "trigger": timedelta(minutes=-30),
                "description": "Rappel visite musée",
            }
        ],
        # "categories": ["WORK", "MEETING"],
        # "transparency": "TRANSPARENT",
    }
    # Exemple de modification complète
    modify_event(event.uid, changes)
    events = get_events()
    return events


if __name__ == "__main__":
    print(principal)
