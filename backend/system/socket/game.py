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
from system.cache.game_room import GameRoomCache
from system.cache.leaderboard import LeaderboardCache
from system.cache.cache import Cache, get_cache_from_app
from system.events.publishers import publish_game_over
from system.constant import MAX_MEMBERS

SPEED = 30
GRAVITY = 0.016
PLAYER_CACHE_EXPIRY = 600
PLAYER_RADIUS = 10
PROJECTILE_RADIUS = 5
DIMENSION_MIN = 10
DIMENSION_MAX = 824

game_room = GameRoomCache()


async def get_rooms():
    pass


# HACK: I am using in memory sessions for storing the user_id and the room token for sids
# on connect is validating all the stuffs from the redis cache and putting them from the redis cache to session
# if server dies -> the client need to reconnect again so again it will get verified
# we can check them from redis cache everytime but its kinda feel weird as it will make a network call

# TODO: Each game room should be a separate server
# HACK: each room has max of 3 players so not that much of a perssure on the server to make calls to the redis server
# same for the leaderboard
# pressure will be with the players movement and projectiles as they are changing continuously


# TODO: Adding syncing game rooms from the cache to the local game_room. Since a single server so not adding
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
        game_room.remove_player(room.room_id,user_id)

    async def sync_player_movement(self, app, room_id):
        players = game_room.get_all_players(room_id)
        players = list(map(lambda player:player.model_dump(),players))
        await self.emit("update-players", players, to=room_id)

    async def sync_projectile_and_collision(self, app, room_id):
        cache = get_cache_from_app(app)
        players_cache = PlayersCache(cache)
        room_cache = RoomCache(cache,room_id)
        leaderboard = LeaderboardCache(cache,room_id)
        projectile_cache = game_room.get_projectile_cache(room_id)
        projectiles = projectile_cache.remove_projectiles(room_id)

        players_map = game_room.get_players_batch(room_id)

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
                        cur_player_element = GameElement(
                            **cur_player.position, radius=PLAYER_RADIUS
                        )
                        projectile_element = GameElement(
                            **projectile.position, radius=PROJECTILE_RADIUS
                        )
                        if check_collision(cur_player_element, projectile_element):
                            await leaderboard.add_score(projectile.user_id)
                            await self.emit('over',{'room_id': room_id},to=cur_player.sid)
                            await self.remove_player(
                                players_cache, room_cache, cur_player.player_id
                            )
                            # if not removed then score will increase by two as player is deleted from the source but is present in the memory
                            game_room.remove_player(room_id,cur_player.player_id)
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
                projectile_cache.push_to_front(room_id,projectile)
        
        await self.emit("update-projectiles", projectile_response, room=room_id)
        if game_room.is_game_started(room_id) and game_room.is_game_completed(room_id):
            await self.emit('over', {'room_id': room_id}, room=room_id)

            players = game_room.get_all_players(room_id)

            # it will be only one player though
            remove_player_tasks = [
                self.remove_player(players_cache, room_cache, player.player_id)
                for player in players
            ]

            projectile_cache.delete(room_id),
            await asyncio.gather(
                RoomCache.remove_room(cache, room_id),
                publish_game_over(room_id),
                *remove_player_tasks
            )
            game_room.delete_room(room_id)

    async def start_game_ticker(self, app):
        while True:
            rooms = game_room.get_rooms()
            for room_id in rooms:
                if game_room.is_game_started(room_id):
                    await self.sync_player_movement(app, room_id)
                    await self.sync_projectile_and_collision(app, room_id)
            await asyncio.sleep(0.015)

    async def sync_game_rooms(self,app):
        cache = get_cache_from_app(app)
        player_cache = PlayersCache(cache)
        while True:
            rooms = game_room.get_rooms()
            for room_id in rooms:
                if game_room.is_game_started(room_id):
                    players = game_room.get_all_players(room_id)
                    await player_cache.set_players_batch(players,ttl=300)
            await asyncio.sleep(30)

    @con_event
    async def on_connect(self, sid, cache: Cache, user_id: str, *args, **kwargs):
        players_cache = PlayersCache(cache)
        player_exists = await players_cache.get_player(user_id)
        if not player_exists:
            raise Exception("Player not existing")
        room_id = player_exists.room_id
        room_cache = RoomCache(cache,room_id)
        room, player_in_room = await asyncio.gather(
            RoomCache.get_room(cache, room_id),
            room_cache.has(user_id)
        )
        if not any((room_id,player_in_room)):
            raise Exception("Game not started")

        if player_in_room and not game_room.get_player(room_id,user_id):
            game_room.set_player(room_id,user_id,player_exists)

        room = RoomCache(cache, room_id)
        # updating the sid as the namespace is changed so adding the new sid
        player_exists.sid = sid
        await players_cache.set_player(player_exists)
        game_room.set_player(room_id,user_id,player_exists)
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
        room_id = session.get("room_id")
        player = game_room.get_player(room_id,user_id)

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
        game_room.set_player(room_id,user_id,player)

    async def on_shoot(self, sid, projectile: dict):
        # scope = self.get_environ(sid).get("asgi.scope")
        app = self.server.environ.get("app")
        session = await self.get_session(sid)
        user_id = session.get("user_id")
        room_id = session.get("room_id")
        user_projectile = Projectile(
            **projectile, user_id=user_id, projectile_id=get_random_id()
        )
        projectile_cache = game_room.get_projectile_cache(room_id)
        projectile_cache.add_projectile(room_id,user_projectile)

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
