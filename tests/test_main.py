from fastapi.testclient import TestClient

import sys
import os

# Ajouter le dossier parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from fastapi.websockets import WebSocket

client = TestClient(app)

BOARD_NAME = "Infra"
BOARD_STACK = "Doing"


def test_websocket():
    with client.websocket_connect("/ws/test-client") as websocket:
        websocket.send_text("Hello WebSocket")
        data = websocket.receive_text()
        assert "Client #test-client dit: Hello WebSocket" in data


def test_websocket_echo():
    with client.websocket_connect("/ws/test-client") as websocket:
        websocket.send_text("Hello WebSocket")
        response = websocket.receive_text()
        assert response == "Client #test-client dit: Hello WebSocket"


def test_healthcheck():
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_get_boards():
    response = client.get("/boards")
    assert response.status_code == 200
    # assert response.json() == {"message": "OK"}


def test_get_board():
    response = client.get(f"/board/{BOARD_NAME}")
    assert response.status_code == 200


def test_get_cards():
    response = client.get(f"/cards/{BOARD_NAME}")
    assert response.status_code == 200


def test_get_stack():
    response = client.get(f"/board/{BOARD_NAME}/stack/{BOARD_STACK}")
    assert response.status_code == 200


# def test_get_stack_by_id():
#     response = client.get(f"/board/{BOARD_NAME}/stack/{BOARD_STACK}")
#     assert response.status_code == 200


def test_get_labels():
    response = client.get(f"/board/{BOARD_NAME}/labels")
    assert response.status_code == 200


def test_get_events():
    response = client.get(f"/events")
    assert response.status_code == 200
    assert response.json()


def test_get_gaps():
    response = client.get(f"/gaps")
    assert response.status_code == 200


def test_get_gaps_2days():
    response = client.get(f"/gaps/2")
    assert response.status_code == 200


def test_sort_by_priority():
    response = client.get(f"/sort-by-priority/{BOARD_NAME}")
    assert response.status_code == 200


def test_get_top_priority():
    response = client.get(f"/top-priority/{BOARD_NAME}")
    assert response.status_code == 200


# def create_event_and_delete():
