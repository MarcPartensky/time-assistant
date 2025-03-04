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

# planification uniquement dans ces zones horaires
DEFAULT_WORK_START = 9
DEFAULT_WORK_END = 20

PLAN_DAYS_LIMIT = 1  # Nombre de jours à planifier

DEFAULT_TASK_DURATION = timedelta(hours=2, minutes=45)  # en heure


class TimeGap(NamedTuple):
    t1: datetime
    t2: datetime

    def __str__(self):
        return "TG" + str((self.t1, self.t2))


# Class TimeGaps(List(TimeGap)):

#     def __


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
        self.work_start = work_start
        self.work_stop = work_stop
        self.calendars = calendars
        self.work_calendar = "Taff"
        self.personal_calendar = "Personal"
        self.zoneinfo = ZoneInfo("Europe/Paris")
        self.priorities = [
            "Top priority",
            "High priority",
            "Action needed",
            "Low priority",
        ]
        self.category = "Deck"  # Tag given on all created events

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

    # def get_gaps(self, t1: datetime, t2: datetime) -> List[TimeGap]:
    #     if t1 >= t2:
    #         return []
    #     events = [
    #         (event.begin.astimezone(self.zoneinfo), event.end.astimezone(self.zoneinfo))
    #         for event in self.events
    #     ]

    #     valid_events = [(s, e) for (s, e) in events if s < e]
    #     sorted_events = sorted(valid_events, key=lambda x: x[0])

    #     # Merging overlapping events
    #     merged = []
    #     for event in sorted_events:
    #         if not merged:
    #             merged.append(event)
    #         else:
    #             last_start, last_end = merged[-1]
    #             current_start, current_end = event
    #             if current_start <= last_end:
    #                 merged[-1] = (last_start, max(last_end, current_end))
    #             else:
    #                 merged.append(event)

    #     # Clip the events starting before t1 and after t2
    #     clipped = []
    #     for start, end in merged:
    #         clipped_start = max(start, t1)
    #         clipped_end = min(end, t2)
    #         if clipped_start < clipped_end:
    #             clipped.append((clipped_start, clipped_end))

    #     gaps = []
    #     prev_end = t1
    #     for start, end in clipped:
    #         if start > prev_end:
    #             gaps.append(TimeGap(prev_end, start))
    #         prev_end = max(prev_end, end)
    #     if prev_end < t2:
    #         gaps.append(TimeGap(prev_end, t2))

    #     return gaps

    def get_gaps(self, t1: datetime, t2: datetime) -> List[P.Interval]:
        """Trouve les disponibilités entre les événements calendrier."""
        if t1 >= t2:
            return []

        # Créer un intervalle global [t1, t2]
        total_interval = P.closed(t1, t2)

        # Créer l'union de tous les événements
        events_union = P.Interval(
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

        return list(gaps) if not gaps.empty else []

    def create_sleep_events(self):
        """Create sleep events"""
        events = []

        today = datetime.today().date()
        begin_of_sleep = datetime.combine(today, datetime.min.time()).astimezone(
            self.zoneinfo
        )  # 00:00:00
        end_of_sleep = begin_of_sleep + timedelta(hours=9)
        gaps = self.get_gaps(begin_of_sleep, end_of_sleep)

        print(end_of_sleep)
        # print(gaps[0][1] - timed)
        first_gap = gaps[0]
        if first_gap[1] - timedelta(hours=1) < end_of_sleep:
            end_of_sleep = first_gap[1] - timedelta(hours=1)
        print(end_of_sleep)

        event = Event(name="Sleep", begin=begin_of_sleep, end=end_of_sleep)

        target_calendar = calendar.get_calendar(self.personal_calendar)

        if not target_calendar:
            raise ValueError(f"Calendar '{self.work_calendar}' not found")

        events.append(event)
        print(event.__dict__)

        vcal = calendar.ics_to_vobject(event)
        ical_data = vcal.serialize()
        target_calendar.add_event(ical_data)

        return events

    def create_deck_events(self):
        events = []
        return events

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

    def create_event(self, card: Card, interval: P.Interval) -> SmartEvent:
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

    def trim_timegaps(self, gaps: List[P.Interval]) -> List[P.Interval]:
        """Filtre les gaps pour ne garder que les heures de travail."""
        if not gaps:
            return []

        # Créer l'union de tous les gaps
        gaps_union = P.Interval(*gaps)

        # Générer les plages horaires de travail
        work_hours = P.empty()
        start_date = min(gap.lower.date() for gap in gaps)
        end_date = max(gap.upper.date() for gap in gaps)

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
        trimmed = gaps_union & work_hours

        return list(trimmed) if not trimmed.empty else []

    # def schedule(self, t1: datetime, t2: datetime) -> List[SmartEvent]:
    #     self.clean_deck_events(t1, t2)
    #     gaps = self.get_gaps(t1, t2)
    #     gaps = self.trim_timegaps(gaps)

    #     if not gaps or not self.cards:
    #         return []

    #     # Aplatir les intervalles composés
    #     atomic_gaps = []
    #     for gap in gaps:
    #         atomic_gaps.extend(gap)

    #     events = []
    #     card_iter = iter(self.cards)

    #     try:
    #         current_card = next(card_iter)
    #         current_duration = self.estimate_duration(current_card)

    #         for gap in atomic_gaps:
    #             remaining_gap = gap.upper - gap.lower
    #             while remaining_gap > timedelta(0):
    #                 if current_duration <= remaining_gap:
    #                     # Créer l'événement complet
    #                     events.append(
    #                         self.create_event(
    #                             current_card, gap.lower, gap.lower + current_duration
    #                         )
    #                     )
    #                     gap = P.closed(gap.lower + current_duration, gap.upper)
    #                     current_card = next(card_iter)
    #                     current_duration = self.estimate_duration(current_card)
    #                     remaining_gap = gap.upper - gap.lower
    #                 else:
    #                     # Utiliser une partie du gap
    #                     events.append(
    #                         self.create_event(
    #                             current_card, gap.lower, gap.lower + remaining_gap
    #                         )
    #                     )
    #                     current_duration -= remaining_gap
    #                     break

    #     except StopIteration:
    #         pass

    #     for event in events:
    #         event.save_to_calendar(self.work_calendar)

    #     return events

    def add_work_breaks(
        self,
        gaps: List[P.Interval],
        work_duration: timedelta = DEFAULT_TASK_DURATION,
        break_duration: timedelta = timedelta(minutes=15),
    ) -> List[P.Interval]:
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

    def schedule(self, t1: datetime, t2: datetime) -> List[SmartEvent]:
        self.clean_deck_events(t1, t2)
        gaps = self.get_gaps(t1, t2)
        gaps = self.trim_timegaps(gaps)
        gaps = self.add_work_breaks(gaps)

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
