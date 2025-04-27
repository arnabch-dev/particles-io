from .cache import Cache


class RoomCache:
    def __init__(self, cache: Cache, room_id: str):
        self.cache = cache
        self.room_id = f"room:{room_id}"

    @classmethod
    async def add_room(cls, cache: Cache, room_id: str):
        async with cache as cache_instance:
            await cache_instance.sadd("rooms", room_id)

    @classmethod
    async def get_all_rooms(cls, cache: Cache):
        async with cache as cache_instance:
            room_ids = await cache_instance.smembers("rooms")
            return list(map(lambda pid: pid.decode("utf-8"), room_ids))

    @classmethod
    async def remove_room(cls, cache: Cache, room_id: str):
        async with cache as cache_instance:
            await cache_instance.srem("rooms", room_id)

    async def add_player(self, player_id: str):
        async with self.cache as cache:
            await cache.sadd(self.room_id, player_id)

    async def remove_player(self, player_id: str):
        async with self.cache as cache:
            await cache.srem(self.room_id, player_id)

    async def get_all_players(self):
        async with self.cache as cache:
            pids = await cache.smembers(self.room_id)
            return list(map(lambda pid: pid.decode("utf-8"), pids))

    async def has(self, player_id):
        if not player_id:
            return False
        async with self.cache as cache:
            return bool(await cache.sismember(self.room_id, player_id))

    async def cleanup_expired_players(self):
        async with self.cache as cache:
            player_ids = await cache.smembers(self.room_id)
            for pid in player_ids:
                if not await cache.exists(f"pid:{pid}"):
                    await cache.srem(self.room_id, pid)

    async def is_valid(self):
        async with self.cache as cache:
            return cache.exists(self.room_id)
