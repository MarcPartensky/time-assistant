from fastapi.testclient import TestClient

import sys
import os

# Ajouter le dossier parent au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from fastapi.websockets import WebSocket

client = TestClient(app)


def test_websocket():
    with client.websocket_connect("/ws/test-client") as websocket:
        websocket.send_text("Hello WebSocket")
        data = websocket.receive_text()
        assert "Client #test-client dit: Hello WebSocket" in data


def test_echo_message():
    test_message = {"text": "Hello FastAPI!"}
    response = client.post("/echo", json=test_message)
    assert response.status_code == 200
    assert response.json() == {"message": test_message["text"]}


def test_websocket_echo():
    with client.websocket_connect("/ws/test-client") as websocket:
        websocket.send_text("Hello WebSocket")
        response = websocket.receive_text()
        assert response == "Client #test-client dit: Hello WebSocket"


def create_event_and_delete():
