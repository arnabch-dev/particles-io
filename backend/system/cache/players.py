from .cache import Cache, serialise_cache_get_data
from system.models import Player


class PlayersCache:
    def __init__(self, cache: Cache):
        self.cache = cache

    async def set_player(self, player: Player, ttl=600):
        async with self.cache as cache:
            await cache.set(f"player:{player.player_id}", player.model_dump_json(), ttl)

    async def get_player(self, player_id: str) -> Player | None:
        async with self.cache as cache:
            value = await cache.get(f"player:{player_id}")
            if not value:
                return None
            value = serialise_cache_get_data(value)
            return Player(**value)

    async def get_players_batch(self, player_ids: list[str]) -> dict[str, Player]:
        keys = [f"player:{pid}" for pid in player_ids]

        async with self.cache as cache:
            values = await cache.mget(keys)

        result = {}
        for pid, value in zip(player_ids, values):
            if value:
                parsed = serialise_cache_get_data(value)
                result[pid] = Player(**parsed)
        return result

    async def delete_player(self, player_id: str):
        async with self.cache as cache:
            await cache.delete(f"player:{player_id}")
