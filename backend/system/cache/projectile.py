from collections import deque, defaultdict
from system.models import Projectile

class ProjectileCache:
    def __init__(self):
        self.cache = defaultdict(deque)

    def add_projectile(self, key: str, projectile: Projectile):
        self.cache[key].append(projectile)

    def remove_projectiles(self, key: str) -> list[Projectile]:
        projectile_queue = self.cache[key]
        projectiles = list(projectile_queue)
        projectile_queue.clear()
        return projectiles

    def push_to_front(self, key: str, projectile: Projectile):
        self.cache[key].appendleft(projectile)

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]

