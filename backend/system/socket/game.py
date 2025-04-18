import asyncio
from socketio import AsyncNamespace
from .utils import dump_player_details, get_velocity, get_random_id, check_collision
from .decorators import con_event
from system.models import PlayerResponse, Projectile, ProjectileResponse, GameElement
from system.cache.room import RoomCache
from system.cache.players import PlayersCache
from system.cache.projectile import ProjectileCache
from system.cache.cache import Cache, get_cache_from_app

SPEED = 30
GRAVITY = 0.016
PLAYER_CACHE_EXPIRY = 600
PLAYER_RADIUS = 10
PROJECTILE_RADIUS = 5
DIMENSION_MIN = 10
DIMENSION_MAX = 824
DEFAULT_ROOM = "ROOM"

class GameNamespace(AsyncNamespace):
    # generally app will be setup during startup event
    def __init__(self, namespace="/game",app=None):
        super().__init__(namespace)
        self.app = app

    def set_app(self,app):
        self.app = app
    async def get_all_player_details(self, players_cache, room) -> list:
        players = []
        all_players_ids = await room.get_all_players()
        for pid in all_players_ids:
            player = await players_cache.get_player(pid)
            if player:
                player = player.model_dump()
                players.append(PlayerResponse(**player).model_dump())
        return players

    async def remove_player(self, players_cache, room, user_id):
        await players_cache.delete_player(user_id)
        await room.remove_player(user_id)

    async def sync_player_movement(self, app):
        cache = get_cache_from_app(app)
        players_cache = PlayersCache(cache)
        room = RoomCache(cache, DEFAULT_ROOM)
        players = await self.get_all_player_details(players_cache, room)
        await self.emit("update-players", players)

    async def sync_projectile_and_collision(self, app):
        cache = get_cache_from_app(app)
        players_cache = PlayersCache(cache)
        projectile_cache = ProjectileCache(cache, DEFAULT_ROOM)
        projectiles = await projectile_cache.remove_projectiles()
        room = RoomCache(cache, DEFAULT_ROOM)

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
                if not (DIMENSION_MIN <= projectile.position["x"] <= DIMENSION_MAX) or not (
                    DIMENSION_MIN <= projectile.position["y"] <= DIMENSION_MAX
                ):
                    projectiles[idx] = None
                    continue
                for cur_player in players_map.values():
                    if projectile.user_id != cur_player.player_id:
                        player_element = GameElement(**cur_player.position, radius=PLAYER_RADIUS)
                        projectile_element = GameElement(**projectile.position, radius=PROJECTILE_RADIUS)
                        if check_collision(player_element, projectile_element):
                            await self.remove_player(players_cache, room, cur_player.player_id)
                            projectiles[idx] = None
                            HIT = True
                            break
                if not HIT:
                    projectile_response.append(
                        ProjectileResponse(**projectile.model_dump(), color=player.color).model_dump()
                    )
                    projectiles[idx] = projectile
            else:
                projectiles[idx] = None

        for projectile in projectiles[::-1]:
            if projectile:
                await projectile_cache.push_to_front(projectile)

        await self.emit("update-projectiles", projectile_response)

    async def start_game_ticker(self, app):
        while True:
            await self.sync_player_movement(app)
            await self.sync_projectile_and_collision(app)
            await asyncio.sleep(0.015)

    @con_event
    async def on_connect(self, sid, cache: Cache, user_id: str,*args,**kwargs):
        room = RoomCache(cache, DEFAULT_ROOM)
        players_cache = PlayersCache(cache)
        player_exists = await room.has(user_id) and await players_cache.get_player(user_id)
        if not player_exists:
            player_details = dump_player_details(sid, user_id, DEFAULT_ROOM)
            await room.add_player(user_id)
            await players_cache.set_player(player_details)

        player_data = await self.get_all_player_details(players_cache, room)
        await self.save_session(sid, {"user_id": user_id})
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
        cache = get_cache_from_app(self.app)
        user_projectile = Projectile(
            **projectile, user_id=user_id, projectile_id=get_random_id()
        )
        projectile_cache = ProjectileCache(cache, DEFAULT_ROOM)
        await projectile_cache.add_projectile(user_projectile)

    async def on_disconnect(self, sid,*args,**kwargs):
        # scope = self.get_environ(sid).get("asgi.scope")
        # scope = self.server.environ.get(sid).get("asgi.scope")
        cache = get_cache_from_app(self.app)
        session = await self.get_session(sid)
        user_id = session.get("user_id")
        players_cache = PlayersCache(cache)
        room = RoomCache(cache, DEFAULT_ROOM)
        await self.remove_player(players_cache, room, user_id)
        players = await self.get_all_player_details(players_cache, room)
        await self.emit("joined", players)
