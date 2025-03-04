#!/usr/bin/env python

# from deck import *
# import time

from fastapi import FastAPI

from app.routes.rest import router as rest_router
from app.routes.websocket import router as websocket_router

app = FastAPI(title="Mon Projet FastAPI avec WebSocket")

# Inclure les routes HTTP et WebSocket
app.include_router(rest_router)
app.include_router(websocket_router)

# Point d'entrée principal
if __name__ == "__main__":
    from granian import Granian
    from granian.constants import Interfaces

    Granian(
        target="app.main:app",
        address="0.0.0.0",
        port=8000,
        log_access=True,
        interface=Interfaces.ASGI,
    ).serve()
