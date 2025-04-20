from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .cache.cache import Cache
from system.socket import socket_app, game_namespace,lobby_namespace
from system.routes.lobby import router as lobby_router
from .events import pub_sub
import asyncio


@asynccontextmanager
async def startup_event(app: FastAPI):
    app.state.cache = Cache()
    # setting up pub sub for disconnected users
    # delete users from the users
    # setting up db
    game_namespace.set_app(app)
    pub_sub.set_pubsub(app.state.cache)
    await pub_sub.start_listening()
    asyncio.create_task(game_namespace.start_game_ticker(app))
    yield
    await pub_sub.close()
    await app.state.cache.close()


def create_app():
    app = FastAPI(lifespan=startup_event)
    app.include_router(lobby_router, prefix="/lobby")
    app.mount("/", app=socket_app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Should be a list, not a string
        allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # Allows all headers
    )

    return app
