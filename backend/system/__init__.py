from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .socket.app import socket_app
from contextlib import asynccontextmanager
from .cache.cache import Cache
from .auth import create_access_token


@asynccontextmanager
async def startup_event(app: FastAPI):
    app.state.cache = Cache()
    # setting up pub sub for disconnected users
    # delete users from the users
    # setting up db
    yield
    await app.state.cache.close()


def create_app():
    app = FastAPI(lifespan=startup_event)

    @app.get("/id")
    def get_token():
        import uuid

        return create_access_token({"sub": str(uuid.uuid4())})

    app.mount("/", app=socket_app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Should be a list, not a string
        allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # Allows all headers
    )

    return app
