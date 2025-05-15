from .cache import Cache

SCORE = 1
TTL = 3600
VIEW_TTL = 1800

class LeaderboardCache:
    def __init__(self, cache: Cache, room_id: str):
        self.cache = cache
        self.name = f"leaderboard:{room_id}"
    
    async def init_leaderboard(self, player_scores:dict):
        async with self.cache as cache:
            mapping = {player: score for player,score in player_scores.items()}
            await cache.zadd(self.name, mapping)
            await cache.expire(self.name, TTL)

    async def add_score(self, player):
        async with self.cache as cache:
            result = await cache.zincrby(self.name, SCORE, player)
            await cache.expire(self.name, TTL)
            return result

    async def get_leaderboard(self):
        async with self.cache as cache:
            scores = {}
            # getting in top score to least score
            for player_id, score in await cache.zrevrange(self.name, 0, -1, withscores=True):
                scores[player_id.decode("utf-8")] = score
            await cache.expire(self.name, VIEW_TTL)
            return scores

    async def remove_leaderboard(self):
        async with self.cache as cache:
            await cache.delete(self.name)