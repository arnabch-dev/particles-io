from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .cache.cache import Cache
from system.socket import socket_app, game_namespace, lobby_namespace
from system.routes.router import router as lobby_router
from system.db import sessionmanager
from .events import pub_sub
import asyncio
import os

frontend_deployed_origin = os.environ.get("FRONTEND_ORIGIN")
origins = [
    "http://localhost:5173"
]
if frontend_deployed_origin:
    origins.append(frontend_deployed_origin)


@asynccontextmanager
async def startup_event(app: FastAPI):
    app.state.cache = Cache()
    # setting up pub sub for disconnected users
    # delete users from the users
    # setting up db
    await sessionmanager.create_tables()
    app.state.db_session = sessionmanager
    game_namespace.set_app(app)
    lobby_namespace.set_app(app)
    pub_sub.set_pubsub(app.state.cache,app.state.db_session)
    await pub_sub.start_listening()
    asyncio.create_task(game_namespace.start_game_ticker(app))
    asyncio.create_task(game_namespace.sync_game_rooms(app))
    yield
    await pub_sub.close()
    await app.state.cache.close()


def create_app():
    app = FastAPI(lifespan=startup_event)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(lobby_router, prefix="/lobby")
    app.mount("/", app=socket_app)

    return app
