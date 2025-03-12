import os
from fastapi import HTTPException
from deck.api import NextCloudDeckAPI
from deck.models import Card, Board, Stack, Label
from requests.auth import HTTPBasicAuth
from app.services.logger import logger
from typing import List

from app.settings import settings

auth = HTTPBasicAuth(settings.nextcloud_user, settings.nextcloud_password)

nc = NextCloudDeckAPI(
    settings.nextcloud_url,
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


def get_boards():
    return nc.get_boards()


def get_board_by_name(board_name: str) -> Board:
    board_id = get_board_id_by_name(board_name)
    return nc.get_board(board_id)


def get_labels_by_board_name(board_name: str) -> List[Label]:
    board_id = get_board_id_by_name(board_name)
    board = nc.get_board(board_id)
    return board.labels


def get_stack_by_board_and_stack_names(board_name: str, stack_name: str) -> Stack:
    board_id = get_board_id_by_name(board_name)
    stack_id = get_stack_id_by_name(board_id, stack_name)
    stack = nc.get_stack(board_id, stack_id)
    return stack


def get_cards_by_board(board: Board) -> List[Card]:
    cards = []
    stacks = nc.get_stacks(board.id)
    for stack in stacks:
        cards.extend(nc.get_cards_from_stack(stack_id=stack.id, board_id=board.id))
    return cards


# def get_cards_of_stack(stack: Stack, board: Board)
#     return nc.get_cards_from_stack(stack.id, board:)


def get_stacks_by_board(board: Board) -> List[Stack]:
    return nc.get_stacks(board.id)


def update_board_label_color(board_name: str, label_name: str, color: str) -> Label:
    board_id = get_board_id_by_name(board_name)
    # stack_id = get_stack_id_by_name(board_id, stack_name)
    label_id = get_label_id_by_name(board_id, label_name)
    if not label_id:
        raise LogException(status_code=500, detail="Label doesn't exist")
    label = nc.get_label(board_id, label_id)
    label = nc.update_label(board_id, label_id, title=label.title, color=color)
    return label


def reorder_card(*args, **kwargs):
    return nc.reorder_card(*args, **kwargs)


def get_top_priority(board_name: str) -> Card:
    """Return the top priority card."""
    board = get_board_by_name(board_name)
    stacks = get_stacks_by_board(board)
    stacks.sort(key=lambda stack: stack.order)
    cards = stacks[0].cards
    cards.sort(key=lambda card: card.order)
    return cards[0]


# def archive_done_tasks(board_name: str) -> List[Card]:
#     """Read all the cards from the board and find the tasks that are done.
#     Then archive them and return them."""
#     # L'API nextcloud deck ne permet pas de manipuler le champs done des cartes.
#     done_cards = []
#     board = get_board_by_name(board_name)
#     stacks = get_stacks_by_board(board)
#     for stack in stacks:
#         card = stack.cards[0]

#     return done_cards


# def archive_completed(board_name, str, stack_name: str):
#     board_id = get_board_id_by_name(board_name)
#     stack_id = get_stack_id_by_name(board_id, stack_name)
#     stack: Stack = nc.get_stack(board_id, stack_id)
#     completed_cards = [card for card in cards if card.]
#     for card in cards:

#         if card
#     stack.cards

#     return stack
