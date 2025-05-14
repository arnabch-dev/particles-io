from .cache import Cache

SCORE = 1
TTL = 3600

class LeaderboardCache:
    def __init__(self, cache: Cache, room_id: str):
        self.cache = cache
        self.name = f"leaderboard:{room_id}"

    async def add_score(self, player):
        async with self.cache as cache:
            result = await cache.zincrby(self.name, SCORE, player)
            await cache.expire(self.name, TTL)
            return result

    async def get_leaderboard(self)->list[tuple[str,int]]:
        async with self.cache as cache:
            return await cache.zrange(self.name, 0, -1, withscores=True)

    async def remove_leaderboard(self):
        async with self.cache as cache:
            await cache.delete(self.name)