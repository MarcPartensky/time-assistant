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
    import os

    from granian import Granian
    from granian.constants import Interfaces

    from dotenv import load_dotenv

    load_dotenv()

    Granian(
        target="app.main:app",
        interface=Interfaces.ASGI,
        address=os.environ["GRANIAN_HOST"],
        port=int(os.environ["GRANIAN_PORT"]),
        log_access=bool(os.environ["GRANIAN_LOG_ACCESS_ENABLED"]),
    ).serve()
