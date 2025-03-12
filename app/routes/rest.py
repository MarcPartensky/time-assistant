from fastapi import APIRouter, HTTPException
from app.models.schemas import Message
from pydantic import BaseModel
from collections import OrderedDict
from typing import List, Tuple
from zoneinfo import ZoneInfo

from app.services.logger import logger

from app.services.deck import nc
import app.services.deck as deck
import app.services.calendar as calendar
from app.services.scheduler import Scheduler

from app.models.interval import Interval

import datetime
import portion as P

from app.settings import settings

ZONEINFO = ZoneInfo(settings.timezone)

router = APIRouter()


def serialize_interval(interval: P.Interval) -> Tuple[str]:
    return (interval.lower.isoformat(), interval.upper.isoformat())


@router.get("/")
async def root():
    return {"message": "Bienvenue dans mon projet FastAPI !"}


@router.get("/live")
async def health():
    return {"message": "OK"}


@router.get("/boards")
async def get_boards():
    return deck.get_boards()


@router.get("/board/{board_name}")
async def get_board(board_name: str):
    return deck.get_board_by_name(board_name)


@router.get("/cards/{board_name}")
async def get_cards(board_name: str):
    board = deck.get_board_by_name(board_name)
    cards = deck.get_cards_by_board(board)
    return cards


# @router.get("/board/{board_name}/stack/{stack_name}")
# async def get_all_stacks():
#     return get_stacks()


@router.get("/board/{board_name}/stack/{stack_name}")
async def get_stack(board_name: str, stack_name: str):
    return deck.get_stack_by_board_and_stack_names(board_name, stack_name)


@router.get("/stack/{stack_id}")
async def get_cards_by_stack_id(stack_id: str):
    boards = nc.get_boards()
    board = boards[0]
    for board in boards:
        stack = nc.get_stacks(board.id)
        if stack:
            break
    return nc.get_stack(stack_id=stack_id, board_id=board.id).cards


@router.get("/board/{board_name}/labels")
async def get_labels(board_name: str):
    return deck.get_labels_by_board_name(board_name)


class Color(BaseModel):
    color: str


@router.post("/board/{board_name}/label/{label_name}")
async def update_board_label_color(board_name: str, label_name: str, color: Color):
    return deck.update_board_label_color(board_name, label_name, color.color)


@router.put("/color")
async def show_color(color: Color):
    return color


@router.get("/all-events")
async def get_all_events():
    events = calendar.get_events()
    for event in events:
        print(event)
    return events


@router.get("/events/{days}")
async def get_events(days: int = 1):
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)
    return scheduler.get_today_events()


@router.get("/gaps")
@router.get("/gaps/{days}")
async def get_gaps(days: int = 1):
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)
    gaps = scheduler.get_gaps(t1, t2)
    return [serialize_interval(gap) for gap in gaps]


@router.get("/trimed-gaps")
@router.get("/trimed-gaps/{days}")
async def get_trimed_gaps(days: int = 1):
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)

    gaps = scheduler.get_gaps(t1, t2)
    print("gaps:")
    print(len(gaps))
    gaps = scheduler.trim_timegaps(gaps)
    print("trimed-gaps:")
    print(len(gaps))

    return [serialize_interval(gap) for gap in gaps]


@router.get("/eat-gaps/{days}")
async def eat_gaps(days: int = 1):
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)

    lunch_interval = scheduler.create_daily_events(
        t1, t2, settings.lunch_start, settings.lunch_end
    )
    dinner_interval = scheduler.create_daily_events(
        t1, t2, settings.dinner_start, settings.dinner_end
    )
    interval = Interval(lunch_interval | dinner_interval)
    print(interval)
    return interval.to_json()


@router.get("/availability/{days}")
async def availability(days: int = 1):
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)
    interval = scheduler.get_availability(t1, t2)
    print(type(interval))

    return interval.to_json()


@router.get("/schedule/{board_name}/{days}")
async def schedule(board_name: str, days: int = 1):
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    board = deck.get_board_by_name(board_name)
    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)

    scheduler.hydrate(board)
    events = scheduler.schedule(t1, t2)

    gaps = scheduler.get_gaps(t1, t2)
    gaps = scheduler.trim_timegaps(gaps)

    return events


@router.get("/modify")
async def modify():
    return calendar.modify_description()


@router.get("/sleep")
async def sleep():
    days = 1
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)

    events = calendar.get_events(t1, t2)
    scheduler = Scheduler(events)
    events = scheduler.create_sleep_events()

    return events


@router.get("/sort-by-priority/{board_name}")
async def sort_by_priority(board_name: str):
    events = calendar.get_events()
    board = deck.get_board_by_name(board_name)
    scheduler = Scheduler(events)
    scheduler.hydrate(board)

    cards = scheduler.sort_card_by_priority()
    return cards


@router.get("/clean/{days}")
async def clean(days: int = 1):
    events = calendar.get_events()
    scheduler = Scheduler(events)
    t1 = datetime.datetime.now(ZONEINFO)
    t2 = t1 + datetime.timedelta(days)
    return scheduler.clean_deck_events(t1, t2)


@router.get("/top-priority/{board_name}")
async def get_top_priority(board_name: str):
    """Return the top priority card to do."""
    return deck.get_top_priority(board_name)


# @router.get("/archive-done-tasks/{board_name}")
# async def archive_done_tasks(board_name: str):
#     return deck.archive_done_tasks(board_name)
