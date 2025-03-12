from datetime import datetime
import portion as P
from zoneinfo import ZoneInfo
from app.settings import settings

# from typing import Iterable


class Interval(P.Interval):
    """Intervalle personnalisé avec un affichage lisible et gestion du timezone."""

    def __init__(self, *args, tz: ZoneInfo = settings.zoneinfo, **kwargs):
        super().__init__(*args, **kwargs)
        self.tz = tz

    # %% Méthodes critiques à surcharger %%#
    def _convert(self, other):
        """Convertit les autres intervalles en instances de notre classe si nécessaire"""
        if isinstance(other, P.Interval) and not isinstance(other, Interval):
            return Interval(other, tz=self.tz)
        return other

    def __or__(self, other):
        return Interval(super().__or__(self._convert(other)), tz=self.tz)

    def __and__(self, other):
        return Interval(super().__and__(self._convert(other)), tz=self.tz)

    def __sub__(self, other):
        return Interval(super().__sub__(self._convert(other)), tz=self.tz)

    def __invert__(self):
        return Interval(super().__invert__(), tz=self.tz)

    def __str__(self) -> str:
        return self.format_intervals()

    def format_intervals(self, date_format: str = "%a %d %b %Y") -> str:
        if self.empty:
            return "∅ (empty interval)"

        days = {}
        for atomic in self:
            start = (
                atomic.lower.astimezone(self.tz)
                if isinstance(atomic.lower, datetime)
                else atomic.lower
            )
            end = (
                atomic.upper.astimezone(self.tz)
                if isinstance(atomic.upper, datetime)
                else atomic.upper
            )

            # Groupement par date
            if isinstance(start, datetime):
                day_key = start.strftime("%Y-%m-%d")
                time_slot = (
                    start.strftime("%H:%M"),
                    end.strftime("%H:%M") if isinstance(end, datetime) else str(end),
                )

                if day_key not in days:
                    days[day_key] = {"date": start, "slots": []}
                days[day_key]["slots"].append(time_slot)

        # Construction de la sortie
        output = []
        for day in sorted(days.values(), key=lambda d: d["date"]):
            date_str = day["date"].strftime(date_format)
            slots = []
            for start, end in day["slots"]:
                slots.append(f"{start} - {end}")
            output.append(f"{date_str}: {', '.join(slots)}")

        return "\n".join(output) or "∅ (no datetime intervals)"

    @classmethod
    def closed(cls, lower, upper):
        tz = None
        if isinstance(lower, datetime) and lower.tzinfo:
            tz = lower.tzinfo
        return cls(P.closed(lower, upper), tz)

    def to_json(self) -> list[tuple[datetime]]:
        """Sérialise l'intervalle en format JSON exploitable."""
        output = []

        for atomic in self:
            start = atomic.lower
            end = atomic.upper

            # Conversion des datetime en ISO format
            def convert(value):
                if isinstance(value, datetime):
                    return value.astimezone(self.tz).isoformat()
                return value

            output.append((convert(start), convert(end)))

        return output
