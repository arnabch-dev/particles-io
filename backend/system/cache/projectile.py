from .cache import Cache, serialise_cache_get_data
from system.models import Projectile


# a queue -> projectile coming and removing
class ProjectileCache:
    def __init__(self, cache: Cache, room_id: str):
        self.cache = cache
        self.projectile_queue_id = f"projectile:{room_id}"

    async def add_projectile(self, projectile: Projectile):
        async with self.cache as cache:
            data = await cache.rpush(
                self.projectile_queue_id, projectile.model_dump_json()
            )

    async def remove_projectiles(self) -> list[Projectile]:
        async with self.cache as cache:
            size = await cache.llen(self.projectile_queue_id)
            projectile_list = await cache.lpop(self.projectile_queue_id, size)
            projectiles = []
            if not projectile_list:
                return projectiles
            for projectile in projectile_list:
                projectile = serialise_cache_get_data(projectile)
                projectiles.append(Projectile(**projectile))
            return projectiles

    async def push_to_front(self, projectile: Projectile):
        async with self.cache as cache:
            await cache.lpush(self.projectile_queue_id, projectile.model_dump_json())
