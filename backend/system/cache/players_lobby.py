from .cache import Cache, serialise_cache_get_data
from system.models import Player


class PlayersLobbyCache:
    def __init__(self, cache: Cache):
        self.cache = cache
        self.name = "lobby"

    async def add_player(self, player_id: str):
        async with self.cache as cache:
            await cache.sadd(self.name, player_id)

    async def has(self, player_id) -> Player | None:
        async with self.cache as cache:
            return bool(await cache.sismember(self.name, player_id))

    async def remove_player(self, player_id) -> Player | None:
        async with self.cache as cache:
            return await cache.srem(self.name, player_id)
