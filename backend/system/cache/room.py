from .cache import Cache


class RoomCache:
    def __init__(self, cache: Cache, room_id: str):
        self.cache = cache
        self.room_id = f"room:{room_id}"

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
        async with self.cache as cache:
            return bool(await cache.sismember(self.room_id, player_id))

    async def cleanup_expired_players(self):
        async with self.cache as cache:
            player_ids = await cache.smembers(self.room_id)
            for pid in player_ids:
                if not await cache.exists(f"pid:{pid}"):
                    await cache.srem(self.room_id, pid)
