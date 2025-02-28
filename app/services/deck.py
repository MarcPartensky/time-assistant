import os
from fastapi import HTTPException
from deck.api import NextCloudDeckAPI
from deck.models import Card, Board, Stack, Label
from requests.auth import HTTPBasicAuth
from app.services.logger import logger
from app.env import *

auth = HTTPBasicAuth(os.environ["NEXTCLOUD_USER"], os.environ["NEXTCLOUD_PASSWORD"])

nc = NextCloudDeckAPI(
    NEXTCLOUD_URL,
    auth,
    ssl_verify=True,
)


class LogException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        logger.error(f"HTTPException {status_code}: {detail}")


def get_board_id_by_name(board_name: str):
    try:
        boards = nc.get_boards()
        for board in boards:
            if board.title == board_name:
                return board.id
        raise ValueError(f"Board with name '{board_name}' not found.")
    except Exception as e:
        raise LogException(status_code=500, detail=str(e))


def get_stack_id_by_name(board_id: str, stack_name: str):
    try:
        stacks = nc.get_stacks(board_id)
        for stack in stacks:
            if stack.title == stack_name:
                return stack.id
        raise ValueError(f"stack with name '{stack_name}' not found.")
    except Exception as e:
        raise LogException(status_code=500, detail=str(e))


def get_label_id_by_name(board_id: str, label_name: str):
    try:
        labels = nc.get_board_labels(board_id)
        for label in labels:
            if label.title == label_name:
                return label.id
        raise ValueError(f"Label with name '{label_name}' not found.")
    except Exception as e:
        raise LogException(status_code=500, detail=str(e))


NEXTCLOUD_BOARD_ID = get_board_id_by_name(str(NEXTCLOUD_BOARD))


def get_boards():
    return nc.get_boards()


def get_board_by_name(board_name: str):
    board_id = get_board_id_by_name(board_name)
    return nc.get_board(board_id)


def get_board_labels(board_name: str):
    board_id = get_board_id_by_name(board_name)
    board = nc.get_board(board_id)
    return board.labels


def get_board_stack_by_name(board_name: str, stack_name: str):
    board_id = get_board_id_by_name(board_name)
    stack_id = get_stack_id_by_name(board_id, stack_name)
    stack = nc.get_stack(board_id, stack_id)
    return stack


def update_board_label_color(board_name: str, label_name: str, color: str):
    board_id = get_board_id_by_name(board_name)
    # stack_id = get_stack_id_by_name(board_id, stack_name)
    label_id = get_label_id_by_name(board_id, label_name)
    if not label_id:
        raise LogException(status_code=500, detail="Label doesn't exist")
    label = nc.get_label(board_id, label_id)
    label = nc.update_label(board_id, label_id, title=label.title, color=color)
    return label


# def archive_completed(board_name, str, stack_name: str):
#     board_id = get_board_id_by_name(board_name)
#     stack_id = get_stack_id_by_name(board_id, stack_name)
#     stack: Stack = nc.get_stack(board_id, stack_id)
#     completed_cards = [card for card in cards if card.]
#     for card in cards:

#         if card
#     stack.cards

#     return stack
