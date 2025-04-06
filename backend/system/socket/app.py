from redis import Redis
import json
import socketio
from .utils import dump_player_details
from .decorators import con_event


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, socketio_path="/socket/")

SPEED = 5
PLAYER_CACHE_EXPIRY = 600

async def cache_get(cache:Redis,key):
    data = await cache.get(key)
    if not data:
        return None
    return json.loads(data.decode("utf-8"))

# the game simulator
async def start_game_ticker(app):
    cache:Redis = app.state.cache
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
async def connect(sid, cache: Redis, user_id: str, *args, **kwargs):
    """Handle new client connection."""
    # TODO: make sure to have queuing logic
    # no new player cant' join a new room
    # so make sure to send all the player details at once to all the players
    existing_player = await cache.get(user_id)

    if existing_player:
        player_data = json.loads(existing_player.decode("utf-8"))
    else:
        player_details = dump_player_details(sid, user_id)

        await cache.set(user_id, player_details.model_dump_json(), PLAYER_CACHE_EXPIRY)
        player_data = {
            "player_id": player_details.player_id,
            "color": player_details.color,
            "position": player_details.position
        }

    await sio.save_session(sid, {"user_id": user_id})
    await sio.emit("joined", player_data)


@sio.event
async def move(sid, direction: str, *args):
    # FIXME: Offload input queue and movement processing to a game loop.
    scope = sio.get_environ(sid).get("asgi.scope")
    cache: Redis = scope.get("app").state.cache.client

    session = await sio.get_session(sid)
    user_id = session.get("user_id")

    player = await cache_get(cache,user_id)
    position = player["position"]

    if direction == "up":
        position["y"] -= SPEED
    elif direction == "down":
        position["y"] += SPEED
    elif direction == "left":
        position["x"] -= SPEED
    elif direction == "right":
        position["x"] += SPEED

    player["position"] = position
    await cache.set(user_id, json.dumps(player), PLAYER_CACHE_EXPIRY)


@sio.event
async def shoot(sid, user_id: str, cache: Redis, *args, **kwargs):
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
