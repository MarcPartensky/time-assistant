from .calendar import SmartEvent, Event
from deck.models import Card, Board, Stack, Label
from typing import List, Tuple, NamedTuple
import portion as P

import vobject

import app.services.deck as deck
import app.services.calendar as calendar

# from pprint import pp as print

from app.services.deck import nc
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import ast

from app.models.interval import Interval
from app.settings import settings

# planification uniquement dans ces zones horaires
DEFAULT_WORK_START = settings.work_start
DEFAULT_WORK_END = settings.work_end

PLAN_DAYS_LIMIT = settings.plan_day_limit  # Nombre de jours à planifier

DEFAULT_TASK_DURATION = timedelta(
    hours=settings.task_duration_hours, minutes=settings.task_duration_minutes
)  # en heure


class Scheduler:
    """Planifie le calendrier par ordre de priorité."""

    def __init__(
        self,
        events: List[SmartEvent],
        work_start: int = DEFAULT_WORK_START,
        work_stop: int = DEFAULT_WORK_END,
        calendars: List[str] = [],
    ):
        self.events = events
        self.calendars = calendars

        self.work_start = work_start
        self.work_stop = work_stop
        self.lunch_start = settings.lunch_start
        self.lunch_end = settings.lunch_end
        self.dinner_start = settings.dinner_start
        self.dinner_end = settings.dinner_end

        self.work_calendar = settings.work_calendar
        self.personal_calendar = settings.personal_calendar
        self.zoneinfo = ZoneInfo(settings.timezone)

        self.priorities = [
            "Top priority",
            "High priority",
            "Action needed",
            "Low priority",
        ]
        self.category = settings.deck_category

    def hydrate(self, board: Board):
        self.board = board
        self.stacks = deck.get_stacks_by_board(self.board)
        self.stacks.sort(key=lambda stack: stack.order)
        self.cards = deck.get_cards_by_board(self.board)
        self.sort_cards()

    def sort_cards(self):
        self.stacks.sort(key=lambda stack: stack.order)
        sorted_cards = []
        for stack in self.stacks:
            cards = stack.cards
            cards.sort(key=lambda card: card.order)
            sorted_cards.extend(cards)
        self.cards = sorted_cards

    def get_gaps(self, t1: datetime, t2: datetime) -> Interval:
        """Trouve les disponibilités entre les événements calendrier."""
        if t1 >= t2:
            return P.empty()

        # Créer un intervalle global [t1, t2]
        total_interval = P.closed(t1, t2)

        # Créer l'union de tous les événements
        events_union = Interval(
            *[
                P.closed(
                    event.begin.astimezone(self.zoneinfo),
                    event.end.astimezone(self.zoneinfo),
                )
                for event in self.events
                if event.begin < event.end
            ]
        )

        # Calculer les gaps = total_interval - events_union
        gaps = total_interval - events_union

        return gaps

    def sort_card_by_priority(self) -> List[Card]:
        """Tri par ordre de priorité"""

        reordered_cards = []

        def value_priority(card: Card):
            if card.labels:
                for index, priority in enumerate(self.priorities):
                    if any(label.title == priority for label in card.labels):
                        return index
            return len(self.priorities)

        for stack in self.stacks:
            cards = [card for card in stack.cards if not card.archived]

            # Trier les cartes par priorité et ordre actuel
            sorted_cards = sorted(
                cards, key=lambda card: (value_priority(card), card.order)
            )

            # Mettre à jour l'ordre de chaque carte via l'API
            for new_order, card in enumerate(sorted_cards, start=1):
                # Appeler l'API pour mettre à jour la carte avec le nouvel ordre
                if card.order == new_order:
                    continue

                print(card.order, "->", new_order, card.title)
                nc.update_card(
                    board_id=self.board.id,
                    stack_id=card.stack_id,
                    card_id=card.id,
                    order=new_order,
                    title=card.title,
                    owner=ast.literal_eval(card.owner)["uid"],
                )

                reordered_cards.append(card)
        self.sort_cards()
        return reordered_cards

    def estimate_duration(self, card: Card) -> timedelta:
        """Return time estimation of card in seconds."""
        return DEFAULT_TASK_DURATION

    def create_event(self, card: Card, interval: Interval) -> SmartEvent:
        """Create new event using a card, t1 and t2."""
        categories = [self.category + str(card.id)]
        if card.labels:
            for label in card.labels:
                if label.title:
                    categories.append(label.title)
        # print("create_event:", t1, t2, card.title)
        return SmartEvent(
            name=card.title,
            begin=interval.lower,
            end=interval.upper,
            description=card.description,
            categories=categories,
            # location="Nouveau lieu",
            # status=None,
            # status="CONFIRMED",
            # alarms=[
            #     DisplayAlarm(
            #         trigger=timedelta(minutes=-15), display_text="allumer le feu"
            #     ),
            # ],
        )

    def clean_deck_events(self, t1: datetime, t2: datetime) -> int:
        """Remove all vcal events that have a Category Deck* (for instance Deck1234)"""
        calendar_obj = calendar.get_calendar(self.work_calendar)
        if not calendar_obj:
            return 0

        # Récupérer les événements existants
        events = calendar_obj.date_search(t1, t2)
        removed_events = 0

        for dav_event in events:
            vevent = dav_event.vobject_instance.vevent
            if hasattr(vevent, "categories"):
                categories = vevent.categories.value
                # Vérifier les catégories commençant par 'Deck'
                if any(cat.strip().startswith(self.category) for cat in categories):
                    removed_events += 1
                    dav_event.delete()
        return removed_events

    def trim_timegaps(self, gaps: Interval) -> Interval:
        """Filtre les gaps pour ne garder que les heures de travail."""
        if gaps.empty:
            return P.empty()

        # Générer les plages horaires de travail
        work_hours = P.empty()
        start_date = min(interval.lower.date() for interval in gaps)
        end_date = max(interval.upper.date() for interval in gaps)

        current_date = start_date
        while current_date <= end_date:
            work_start = datetime.combine(
                current_date, time(hour=self.work_start)
            ).replace(tzinfo=self.zoneinfo)

            work_end = datetime.combine(
                current_date, time(hour=self.work_stop)
            ).replace(tzinfo=self.zoneinfo)

            work_hours |= P.closed(work_start, work_end)
            current_date += timedelta(days=1)

        # Intersection entre les gaps et les heures de travail
        trimmed = gaps & work_hours

        return trimmed

    def add_work_breaks(
        self,
        gaps: List[Interval],
        work_duration: timedelta = DEFAULT_TASK_DURATION,
        break_duration: timedelta = timedelta(minutes=15),
    ) -> List[Interval]:
        """Découpe les plages horaires en ajoutant des pauses régulières."""
        new_gaps = []

        for gap in gaps:
            current_start = gap.lower
            total_duration = gap.upper - gap.lower

            # Calculer le nombre de cycles complets travail/pause
            full_cycles = total_duration // (work_duration + break_duration)
            remaining_time = total_duration % (work_duration + break_duration)

            # Générer les intervalles de travail avec pauses
            for _ in range(full_cycles):
                work_end = current_start + work_duration
                new_gaps.append(P.closed(current_start, work_end))
                current_start = work_end + break_duration

            # Ajouter le temps restant inférieur à un cycle complet
            if remaining_time > timedelta(0):
                new_gaps.append(P.closed(current_start, current_start + remaining_time))

        return new_gaps

    def schedule(
        self,
        t1: datetime,
        t2: datetime,
    ) -> List[SmartEvent]:
        self.clean_deck_events(t1, t2)
        gaps = self.get_gaps(t1, t2)
        lunch_interval = self.create_daily_events(
            t1, t2, settings.lunch_start, settings.lunch_end
        )
        dinner_interval = self.create_daily_events(
            t1, t2, settings.dinner_start, settings.dinner_end
        )
        eat_interval = lunch_interval | dinner_interval
        print("eat interval:", eat_interval)
        gaps -= eat_interval
        # gaps = self.trim_timegaps(gaps + lunch_gaps + dinner_gaps)
        # gaps |= self.add_work_breaks(gaps)

        if not gaps or not self.cards:
            return []

        # Aplatir les intervalles composés
        atomic_gaps = []
        for gap in gaps:
            atomic_gaps.extend(gap)

        events = []
        card_iter = iter(self.cards)

        try:
            current_card = next(card_iter)
            current_duration = self.estimate_duration(current_card)

            for gap in atomic_gaps:
                remaining_gap = gap.upper - gap.lower
                while remaining_gap > timedelta(0):
                    if current_duration <= remaining_gap:
                        # Créer l'événement complet
                        events.append(
                            self.create_event(
                                current_card,
                                P.closed(gap.lower, gap.lower + current_duration),
                            )
                        )
                        gap = P.closed(gap.lower + current_duration, gap.upper)
                        current_card = next(card_iter)
                        current_duration = self.estimate_duration(current_card)
                        remaining_gap = gap.upper - gap.lower
                    else:
                        # Utiliser une partie du gap
                        events.append(
                            self.create_event(
                                current_card,
                                P.closed(gap.lower, gap.lower + remaining_gap),
                            )
                        )
                        current_duration -= remaining_gap
                        break

        except StopIteration:
            pass

        for event in events:
            event.save_to_calendar(self.work_calendar)
        return events

    def create_daily_events(
        self,
        t1: datetime,
        t2: datetime,
        g1: int,
        g2: int,
    ) -> Interval:
        """Create daily events in the schedule."""
        daily_events = P.empty()
        current_date = t1.date()
        end_date = t2.date()

        while current_date <= end_date:
            # Create daily start and end times for the current date
            daily_start_time = time(hour=g1)
            daily_end_time = time(hour=g2)
            daily_start_dt = datetime.combine(current_date, daily_start_time).replace(
                tzinfo=self.zoneinfo
            )
            daily_end_dt = datetime.combine(current_date, daily_end_time).replace(
                tzinfo=self.zoneinfo
            )

            # Adjust daily_end_dt if it's on the next day
            if daily_end_dt <= daily_start_dt:
                daily_end_dt += timedelta(days=1)

            # Create the interval for the current day's daily
            day_daily_interval = P.closed(daily_start_dt, daily_end_dt)

            # Intersect with the overall time range [t1, t2]
            valid_interval = day_daily_interval & P.closed(t1, t2)

            if not valid_interval.empty:
                daily_events |= valid_interval

            current_date += timedelta(days=1)

        return daily_events

    def create_sleep_events(self, t1: datetime, t2: datetime) -> Interval:
        """Create sleep events"""
        sleep_events = self.create_daily_events(t1, t2, 0, settings.work_start)
        # events = self.create_daily_events(t1, t2, settings.work_end, 24)
        return sleep_events
