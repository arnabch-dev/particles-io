import redis.asyncio as redis
from fastapi import Request,FastAPI
class Cache:
    def __init__(self, redis_url: str = "redis://localhost:6379", pool_size: int = 5):
        self.pool = redis.ConnectionPool.from_url(redis_url, max_connections=pool_size)
        self.client:redis.Redis = redis.Redis(connection_pool=self.pool, decode_responses=True)  # Decode to string

    async def close(self):
        """Close Redis connection."""
        print("closing")
        await self.client.close()

def get_cache_from_request(request:Request) ->redis.Redis:
    return request.app.state.cache.client

def get_cache_from_app(app:FastAPI) ->redis.Redis:
    return app.state.cache.client