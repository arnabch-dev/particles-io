import asyncio
import socketio
from .utils import dump_player_details
from .decorators import con_event
from system.models import PlayerResponse, Projectile, ProjectileResponse
from system.cache.room import RoomCache
from system.cache.players import PlayersCache
from system.cache.projectile import ProjectileCache
from system.cache.cache import Cache, get_cache_from_app

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, socketio_path="/socket/")

SPEED = 5
PLAYER_CACHE_EXPIRY = 600
DEFAULT_ROOM = "ROOM"


async def get_all_player_details(players_cache, room):
    players = []
    all_players_ids = await room.get_all_players()
    for pid in all_players_ids:
        player = await players_cache.get_player(pid)
        if player:
            player = player.model_dump()
            players.append(PlayerResponse(**player).model_dump())
    return players


async def sync_player_movement(app):
    cache = get_cache_from_app(app)
    players_cache = PlayersCache(cache)
    room = RoomCache(cache, DEFAULT_ROOM)
    players = await get_all_player_details(players_cache, room)
    await sio.emit("update-players", players)

async def sync_projectile(app):
    cache = get_cache_from_app(app)
    players_cache = PlayersCache(cache)
    projectile_cache = ProjectileCache(cache,DEFAULT_ROOM)
    projectiles = await projectile_cache.remove_projectiles()
    projectile_response = []
    for projectile in projectiles:
        player = await players_cache.get_player(projectile.user_id)
        if player:
            projectile_response.append(ProjectileResponse(**projectile.model_dump(),color=player.color).model_dump())
    await sio.emit("update-projectiles",projectile_response)

# the game simulator(15 ms)
# Halflife uses 66.66 ticks per second
# so in
async def start_game_ticker(app):
    # TODO: filter keys with prefix and namespace
    while True:
        await sync_player_movement(app)
        await sync_projectile(app)
        await asyncio.sleep(0.015)


@sio.event
@con_event
async def connect(sid, cache: Cache, user_id: str, *args, **kwargs):
    """Handle new client connection."""
    # TODO: make sure to have queuing logic
    # no new player cant' join a new room
    # so make sure to send all the player details at once to all the players

    room = RoomCache(cache, DEFAULT_ROOM)
    players_cache = PlayersCache(cache)
    player_exists = await room.has(user_id) and await players_cache.get_player(user_id)
    if not player_exists:
        player_details = dump_player_details(sid, user_id, DEFAULT_ROOM)
        await room.add_player(user_id)
        await players_cache.set_player(player_details)

    player_data = await get_all_player_details(players_cache, room)
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
async def shoot(sid, projectile: dict, *args, **kwargs):
    scope = sio.get_environ(sid).get("asgi.scope")
    app = scope.get("app")
    session = await sio.get_session(sid)
    user_id = session.get("user_id")
    cache = get_cache_from_app(app)
    user_projectile = Projectile(**projectile, user_id=user_id)
    projectile_cache = ProjectileCache(cache, DEFAULT_ROOM)
    await projectile_cache.add_projectile(user_projectile)


@sio.event
async def disconnect(sid, *args):
    """
    Handle client disconnection.
    TODO: Clean up player from cache or mark offline.
    FIXME: add a secondary reconnect cache with ttl -> move player from room to there
    """
    scope = sio.get_environ(sid).get("asgi.scope")
    app = scope.get("app")
    cache = get_cache_from_app(app)
    session = await sio.get_session(sid)
    user_id = session.get("user_id")
    players_cache = PlayersCache(cache)
    room = RoomCache(cache, DEFAULT_ROOM)
    await players_cache.delete_player(user_id)
    await room.remove_player(user_id)
    players = await get_all_player_details(players_cache, room)
    await sio.emit("joined", players)
