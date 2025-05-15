import asyncio
from socketio import AsyncNamespace
from .utils import (
    dump_player_details,
    get_velocity,
    get_random_id,
    check_collision,
    get_all_player_details,
)
from system.sio import sio
from .decorators import con_event
from system.models import Projectile, ProjectileResponse, GameElement
from system.cache.room import RoomCache
from system.cache.players import PlayersCache
from system.cache.projectile import ProjectileCache
from system.cache.leaderboard import LeaderboardCache
from system.cache.cache import Cache, get_cache_from_app
from system.db import get_db_session_from_app
from system.events.publishers import publish_game_over

SPEED = 30
GRAVITY = 0.016
PLAYER_CACHE_EXPIRY = 600
PLAYER_RADIUS = 10
PROJECTILE_RADIUS = 5
DIMENSION_MIN = 10
DIMENSION_MAX = 824


async def get_rooms():
    pass


# HACK: I am using in memory sessions for storing the user_id and the room token for sids
# on connect is validating all the stuffs from the redis cache and putting them from the redis cache to session
# if server dies -> the client need to reconnect again so again it will get verified
# we can check them from redis cache everytime but its kinda feel weird as it will make a network call
class GameNamespace(AsyncNamespace):
    # generally app will be setup during startup event
    def __init__(self, namespace="/game", app=None):
        super().__init__(namespace)
        self.app = app

    def set_app(self, app):
        self.app = app

    async def remove_player(self, players_cache, room, user_id):
        await players_cache.delete_player(user_id)
        await room.remove_player(user_id)

    async def sync_player_movement(self, app, room_id):
        cache = get_cache_from_app(app)
        players_cache = PlayersCache(cache)
        room = RoomCache(cache, room_id)
        players = await get_all_player_details(players_cache, room)
        await self.emit("update-players", players, to=room_id)

    async def sync_projectile_and_collision(self, app, room_id):
        cache = get_cache_from_app(app)
        db_session = get_db_session_from_app(app)
        players_cache = PlayersCache(cache)
        leaderboard = LeaderboardCache(cache,room_id)
        projectile_cache = ProjectileCache(cache, room_id)
        projectiles = await projectile_cache.remove_projectiles()
        room = RoomCache(cache, room_id)

        player_ids = await room.get_all_players()
        players_map = await players_cache.get_players_batch(list(player_ids))

        projectile_response = []
        for idx, projectile in enumerate(projectiles):
            HIT = False
            player = players_map.get(projectile.user_id)
            x, y = get_velocity(projectile.angle, 4)

            if player:
                projectile.position["x"] += x
                projectile.position["y"] += y + GRAVITY
                if not (
                    DIMENSION_MIN <= projectile.position["x"] <= DIMENSION_MAX
                ) or not (DIMENSION_MIN <= projectile.position["y"] <= DIMENSION_MAX):
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
                            await leaderboard.add_score(cur_player.player_id)
                            await self.remove_player(
                                players_cache, room, cur_player.player_id
                            )
                            # if not removed then score will increase by two as player is deleted from the source but is present in the memory
                            del players_map[cur_player.player_id]
                            projectiles[idx] = None
                            HIT = True
                            break
                if not HIT:
                    projectile_response.append(
                        ProjectileResponse(
                            **projectile.model_dump(), color=player.color
                        ).model_dump()
                    )
                    projectiles[idx] = projectile
            else:
                projectiles[idx] = None

        for projectile in projectiles[::-1]:
            if projectile:
                await projectile_cache.push_to_front(projectile)
        
        player_count = await room.get_player_count()
        await self.emit("update-projectiles", projectile_response, to=room_id)
        if player_count <= 1:
            await self.emit('over', {'room_id': room_id}, to=room_id)

            players = await room.get_all_players()

            # it will be only one player though
            remove_player_tasks = [
                self.remove_player(players_cache, room, player_id)
                for player_id in players
            ]

            await asyncio.gather(
                RoomCache.remove_room(cache, room_id),
                projectile_cache.delete(),
                publish_game_over(room_id),
                *remove_player_tasks
            )

    async def start_game_ticker(self, app):
        cache = get_cache_from_app(app)
        while True:
            rooms = await RoomCache.get_all_rooms(cache)
            for room_id in rooms:
                await self.sync_player_movement(app, room_id)
                await self.sync_projectile_and_collision(app, room_id)
            await asyncio.sleep(0.015)

    @con_event
    async def on_connect(self, sid, cache: Cache, user_id: str, *args, **kwargs):
        players_cache = PlayersCache(cache)
        player_exists = await players_cache.get_player(user_id)
        if not player_exists:
            raise Exception("Player not existing")
        room_id = player_exists.room_id
        if not await RoomCache.get_room(cache, room_id):
            raise Exception("Game not started")
        room = RoomCache(cache, room_id)
        await self.enter_room(sid, room=room_id, namespace=self.namespace)
        player_data = await get_all_player_details(players_cache, room)
        await self.save_session(sid, {"user_id": user_id, "room_id": room_id})
        await self.emit("joined", player_data)

    async def on_move(self, sid, direction: str):
        # scope = self.get_environ(sid).get("asgi.scope")
        # scope = self.server.environ.get("asgi.scope")
        # app = scope.get("app")
        session = await self.get_session(sid)
        user_id = session.get("user_id")

        cache = get_cache_from_app(self.app)
        players = PlayersCache(cache)
        player = await players.get_player(user_id)

        position = player.position

        if direction == "up":
            position["y"] = max(position["y"] - SPEED, DIMENSION_MIN)
        elif direction == "down":
            position["y"] = min(position["y"] + SPEED, DIMENSION_MAX)
        elif direction == "left":
            position["x"] = max(position["x"] - SPEED, DIMENSION_MIN)
        elif direction == "right":
            position["x"] = min(position["x"] + SPEED, DIMENSION_MAX)

        player.position = position
        await players.set_player(player)

    async def on_shoot(self, sid, projectile: dict):
        # scope = self.get_environ(sid).get("asgi.scope")
        app = self.server.environ.get("app")
        session = await self.get_session(sid)
        user_id = session.get("user_id")
        room_id = session.get("room_id")
        cache = get_cache_from_app(self.app)
        user_projectile = Projectile(
            **projectile, user_id=user_id, projectile_id=get_random_id()
        )
        projectile_cache = ProjectileCache(cache, room_id)
        await projectile_cache.add_projectile(user_projectile)

    async def on_disconnect(self, sid, *args, **kwargs):
        # scope = self.get_environ(sid).get("asgi.scope")
        # scope = self.server.environ.get(sid).get("asgi.scope")
        # cache = get_cache_from_app(self.app)
        # session = await self.get_session(sid)
        # user_id = session.get("user_id")
        # players_cache = PlayersCache(cache)
        # room = RoomCache(cache, DEFAULT_ROOM)
        # await self.remove_player(players_cache, room, user_id)
        # players = await get_all_player_details(players_cache, room)
        # await self.emit("joined", players)
        return
