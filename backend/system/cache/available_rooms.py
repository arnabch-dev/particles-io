from .cache import Cache, serialise_cache_get_data
from system.models import Player
from system.constant import MAX_MEMBERS

SCORE_OF_ROOM = 1


class AvailableRoomsCache:
    def __init__(self, cache: Cache):
        self.cache = cache
        self.name = "available_rooms"

    async def is_room_exists(self, room_id) -> bool:
        async with self.cache as cache:
            return bool(await cache.zscore(self.name, room_id))

    async def add_room(self, room_id) -> int:
        async with self.cache as cache:
            return await cache.zincrby(self.name, SCORE_OF_ROOM, room_id)

    async def increment_room_score_till_threshold(self, room_id):
        f"""Increment by {SCORE_OF_ROOM}. If reached {MAX_MEMBERS} then it removes the room"""
        score = await self.add_room(room_id)
        if score == MAX_MEMBERS:
            await self.remove_room(room_id)
            return -1
        return score

    async def get_room_with_most_player(self) -> tuple[str, int]:
        async with self.cache as cache:
            # use 0,-1 to get all rooms
            room = await cache.zrevrange(self.name, 0, 0, withscores=True)
            if not room:
                return None
            room_id, score = room[0]
            return room_id.decode("utf-8"), score

    async def get_room_with_least_player(self) -> tuple[str, int]:
        async with self.cache as cache:
            # use 0,-1 to get all rooms
            room = await cache.zrange(self.name, 0, 0, withscores=True)
            if not room:
                return None
            room_id, score = room[0]
            return room_id.decode("utf-8"), score

    async def remove_room(self, room_id):
        async with self.cache as cache:
            await cache.zrem(self.name, room_id)
