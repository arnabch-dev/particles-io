import json
import socketio
from .utils import dump_player_details
from .decorators import con_event
from system.models import PlayerResponse
from system.cache.room import RoomCache
from system.cache.players import PlayersCache
from system.cache.cache import Cache, get_cache_from_app

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, socketio_path="/socket/")

SPEED = 5
PLAYER_CACHE_EXPIRY = 600
DEFAULT_ROOM = "ROOM"


# the game simulator
async def start_game_ticker(app):
    cache = get_cache_from_app(app)
    # TODO: filter keys with prefix and namespace
    players = []
    while True:
        keys = await cache.keys("*")
        if keys:
            for key in keys:
                data = await cache.get(key)
                players.append(json.loads(data.decode("utf-8")))


@sio.event
@con_event
async def connect(sid, cache: Cache, user_id: str, *args, **kwargs):
    """Handle new client connection."""
    # TODO: make sure to have queuing logic
    # no new player cant' join a new room
    # so make sure to send all the player details at once to all the players

    room = RoomCache(cache, DEFAULT_ROOM)
    players = PlayersCache(cache)
    # def get_all_player_details():
    player_exists = await room.has(user_id)
    player_data = None
    if player_exists:
        player_data = await players.get_player(user_id)
    
    if not player_data:
        player_details = dump_player_details(sid, user_id, DEFAULT_ROOM)
        player_data = player_details
        await room.add_player(user_id)
        await players.set_player(player_details)
    
    player_data = player_data.model_dump()
    player_data = PlayerResponse(**player_data).model_dump()
    await sio.save_session(sid, {"user_id": user_id})
    await sio.emit("joined", player_data)


@sio.event
async def move(sid, direction: str, *args):
    # FIXME: We could have also used headers from scope to extract token
    # FIXME: Offload input queue and movement processing to a game loop.
    scope = sio.get_environ(sid).get("asgi.scope")
    app = scope.get("app")
    session = await sio.get_session(sid)
    user_id = session.get("user_id")

    cache = get_cache_from_app(app)
    players = PlayersCache(cache)
    player = await players.get_player(user_id)

    position = player.position

    if direction == "up":
        position["y"] -= SPEED
    elif direction == "down":
        position["y"] += SPEED
    elif direction == "left":
        position["x"] -= SPEED
    elif direction == "right":
        position["x"] += SPEED

    player.position = position

    await players.set_player(player)


@sio.event
async def shoot(sid, *args, **kwargs):
    """
    Handle shooting input from client.
    TODO: Implement projectile logic.
    """
    pass


@sio.event
async def disconnect(sid, *args):
    """
    Handle client disconnection.
    TODO: Clean up player from cache or mark offline.
    """
    session = await sio.get_session(sid)
    return session.get("user_id", "unknown")
