from .cache import Cache, serialise_cache_get_data
from system.models import Player


class PlayersLobby:
    def __init__(self, cache: Cache):
        self.cache = cache
        self.name = "lobby"

    async def add_player(self, player_id: str):
        async with self.cache as cache:
            await cache.rpush(self.name, player_id)

    async def get_player(self) -> Player | None:
        async with self.cache as cache:
            return await cache.rpop(self.name, 1)
