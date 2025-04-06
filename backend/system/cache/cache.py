import redis.asyncio as redis
from fastapi import Request, FastAPI
import json


class Cache:
    def __init__(self, redis_url: str = "redis://localhost:6379", pool_size: int = 5):
        self.pool = redis.ConnectionPool.from_url(redis_url, max_connections=pool_size)
        self.client: redis.Redis = redis.Redis(
            connection_pool=self.pool, decode_responses=True
        )  # Decode to string

    async def __aenter__(self, *args, **kwargs):
        return self.client

    async def __aexit__(self, *args, **kwargs):
        # not closing it here as mainly the cache will used indrectly via the stored connection in the app instance
        # await self.close()
        return

    async def close(self):
        print("closing Redis connection")
        await self.client.close()


def get_cache_from_request(request: Request) -> Cache:
    return request.app.state.cache


def get_cache_from_app(app: FastAPI) -> Cache:
    return app.state.cache


def serialise_cache_get_data(data):
    return json.loads(data.decode("utf-8"))
