from .cache import Cache, serialise_cache_get_data
from system.models import Player


class PlayersCache:
    def __init__(self, cache: Cache):
        self.cache = cache

    async def set_player(self, player: Player, ttl=600):
        async with self.cache as cache:
            await cache.set(f"player:{player.player_id}", player.model_dump_json(), ttl)

    async def get_player(self, player_id: str) -> Player:
        async with self.cache as cache:
            value = await cache.get(f"player:{player_id}")
            value = serialise_cache_get_data(value)
            return Player(**value)

    async def delete_player(self, player_id: str):
        async with self.cache as cache:
            await cache.delete(f"player:{player_id}")
