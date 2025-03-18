from ics import Event
import caldav
from typing import Optional
import vobject
from datetime import datetime

from app.settings import settings


def get_calendar(name: str) -> Optional[caldav.Calendar]:
    """Get calendar by name using list comprehension"""
    return next((c for c in settings.calendars if c.name == name), None)


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

    # @rrule.setter
    def set_rrule(self, rrule):
        self._rrule = rrule

    def save_to_calendar(self, calendar_name: str):
        """Sauvegarde dans un calendrier"""
        calendar = get_calendar(calendar_name)
        if not calendar:
            return False
        vcal = self.to_vobject()
        data = vcal.serialize()
        calendar.add_event(data)
        return True

    def __str__(self):
        t = "SmartEvent("
        t += self.begin.strftime("%m-%d %H:%M") + ", "
        t += self.end.strftime("%m-%d %H:%M") + ", "
        t += self.name
        t += ")"
        return t

    def to_vobject(self) -> vobject.base.Component:
        """Convertit un événement ICS.py en VCALENDAR avec gestion des types"""
        vcal = vobject.iCalendar()
        vevent = vcal.add("vevent")

        # Propriétés obligatoires avec conversion explicite
        vevent.add("uid").value = str(self.uid)
        vevent.add("dtstamp").value = datetime.now(settings.zoneinfo)
        vevent.add("summary").value = str(self.name)

        vevent.add("dtstart").value = self.begin.datetime
        if self.end:
            vevent.add("dtend").value = self.end.datetime

        if self.sequence:
            vevent.add("sequence").value = str(self.sequence)

        if self.description:
            vevent.add("description").value = str(self.description)

        if self.location:
            vevent.add("location").value = str(self.location)

        if self.categories:
            # print("categories:")
            # print(self.categories)
            # print(type(self.categories))
            # vevent.add("categories").value = ",".join(map(str, tuple(self.categories)))
            vevent.add("categories").value = self.categories

        if hasattr(self, "status"):
            if self.status:
                vevent.add("status").value = self.status

        if hasattr(self, "transparent"):
            vevent.add("transp").value = "TRANSPARENT" if self.transparent else "OPAQUE"

        return vcal

        # # Géolocalisation avec formatage contrôlé
        if hasattr(self, "geo"):
            if self.geo:
                if self.geo.latitude and self.geo.longitude:
                    geo_value = f"{float(self.geo.latitude):.6f};{float(self.geo.longitude):.6f}"
                    vevent.add("geo").value = geo_value

        if hasattr(self, "rrule"):
            rrule_str = str(self.rrule).replace("RRULE:", "")
            vevent.add("rrule").value = rrule_str

        if hasattr(self, "exdates"):
            if self.exdates:
                for exdate in self.exdates:
                    exdate_prop = vevent.add("exdate")
                    exdate_prop.value = exdate.astimezone(gettz("UTC"))

        # # Alarmes avec vérification de type
        for alarm in self.alarms:
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
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, list):
                    value = ",".join(map(str, value))
                vevent.add(prop).value = str(value)

        # Validation avant sauvegarde
        if len(vevent.contents.get("dtstart", [])) > 1:
            raise ValueError("Multiple DTSTART properties detected")

        return vcal


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
