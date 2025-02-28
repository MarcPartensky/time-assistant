from fastapi import APIRouter, HTTPException
from app.models.schemas import Message
from pydantic import BaseModel
from collections import OrderedDict
from typing import List

from app.services.logger import logger
import app.services.deck as deck
import app.services.calendar as calendar


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Bienvenue dans mon projet FastAPI !"}


@router.post("/echo")
async def echo_message(message: Message):
    return {"message": message.text}


@router.get("/boards")
async def get_all_boards():
    return deck.get_boards()


@router.get("/board/{board_name}")
async def get_board(board_name: str):
    return deck.get_board_by_name(board_name)


# @router.get("/board/{board_name}/stack/{stack_name}")
# async def get_all_stacks():
#     return get_stacks()


@router.get("/board/{board_name}/stack/{stack_name}")
async def get_stack(board_name: str, stack_name: str):
    return deck.get_board_stack_by_name(board_name, stack_name)


@router.get("/board/{board_name}/labels")
async def get_labels(board_name: str):
    return deck.get_board_labels(board_name)


class Color(BaseModel):
    color: str


@router.post("/board/{board_name}/label/{label_name}")
async def update_board_label_color(board_name: str, label_name: str, color: Color):
    return deck.update_board_label_color(board_name, label_name, color.color)


@router.put("/color")
async def show_color(color: Color):
    return color


@router.get("/events")
async def get_events():
    return calendar.get_events()


@router.get("/modify")
async def get_events():
    return calendar.modify_description()
