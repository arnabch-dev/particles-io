import asyncio
import socketio
from .utils import dump_player_details, get_velocity, get_random_id, check_collision
from .decorators import con_event
from system.models import PlayerResponse, Projectile, ProjectileResponse, GameElement
from system.cache.room import RoomCache
from system.cache.players import PlayersCache
from system.cache.projectile import ProjectileCache
from system.cache.cache import Cache, get_cache_from_app

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, socketio_path="/socket/")

SPEED = 30
GRAVITY = 0.016
PLAYER_CACHE_EXPIRY = 600
PLAYER_RADIUS = 10
PROJECTILE_RADIUS = 5
DIMENSION = 1024
DEFAULT_ROOM = "ROOM"


async def get_all_player_details(players_cache, room) -> list:
    players = []
    all_players_ids = await room.get_all_players()
    for pid in all_players_ids:
        player = await players_cache.get_player(pid)
        if player:
            player = player.model_dump()
            players.append(PlayerResponse(**player).model_dump())
    return players


async def remove_player(players_cache, room, user_id):
    await players_cache.delete_player(user_id)
    await room.remove_player(user_id)


async def sync_player_movement(app):
    cache = get_cache_from_app(app)
    players_cache = PlayersCache(cache)
    room = RoomCache(cache, DEFAULT_ROOM)
    players = await get_all_player_details(players_cache, room)
    await sio.emit("update-players", players)


async def sync_projectile_and_collision(app):
    cache = get_cache_from_app(app)
    players_cache = PlayersCache(cache)
    projectile_cache = ProjectileCache(cache, DEFAULT_ROOM)
    projectiles = await projectile_cache.remove_projectiles()
    room = RoomCache(cache, DEFAULT_ROOM)

    player_ids = await room.get_all_players()
    players_map = await players_cache.get_players_batch([*(uid for uid in player_ids)])

    projectile_response = []
    for idx, projectile in enumerate(projectiles):
        HIT = False
        player = players_map.get(projectile.user_id)
        x, y = get_velocity(projectile.angle, 4)

        if player:
            projectile.position["x"] += x
            projectile.position["y"] += y + GRAVITY
            if (
                abs(projectile.position["x"]) >= DIMENSION
                or abs(projectile.position["y"]) >= DIMENSION
            ):
                projectiles[idx] = None
                continue
            for cur_player in players_map.values():
                if projectile.user_id != cur_player.player_id:
                    player_element = GameElement(
                        **cur_player.position, radius=PLAYER_RADIUS
                    )
                    projectile_element = GameElement(
                        **projectile.position, radius=PROJECTILE_RADIUS
                    )
                    if check_collision(player_element, projectile_element):
                        await remove_player(players_cache, room, cur_player.player_id)
                        projectiles[idx] = None
                        HIT = True
                        continue
            if not HIT:
                projectile_response.append(
                    ProjectileResponse(
                        **projectile.model_dump(), color=player.color
                    ).model_dump()
                )
                projectiles[idx] = projectile
        else:
            projectiles[idx] = None
    # Push updated projectiles back to the front of the queue
    for projectile in projectiles[::-1]:
        if projectile:
            await projectile_cache.push_to_front(projectile)

    await sio.emit("update-projectiles", projectile_response)


# the game simulator(15 ms)
# Halflife uses 66.66 ticks per second
# so in
async def start_game_ticker(app):
    # TODO: filter keys with prefix and namespace
    while True:
        await sync_player_movement(app)
        await sync_projectile_and_collision(app)
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
    user_projectile = Projectile(
        **projectile, user_id=user_id, projectile_id=get_random_id()
    )
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
    await remove_player(players_cache, room, user_id)
    players = await get_all_player_details(players_cache, room)
    await sio.emit("joined", players)
