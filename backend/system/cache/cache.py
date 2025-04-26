import redis.asyncio as redis
from fastapi import Request, FastAPI
import json, uuid
from contextlib import asynccontextmanager


class Cache:
    def __init__(self, redis_url: str = "redis://localhost:6379", pool_size: int = 5):
        self.pool = redis.ConnectionPool.from_url(redis_url, max_connections=pool_size)
        self.client: redis.Redis = redis.Redis(
            connection_pool=self.pool, decode_responses=True
        )  # Decode to string

    @asynccontextmanager
    async def transaction_per_key(self, lock_key=None, lock_timeout=5000):
        identifier = None
        print(lock_key)
        # acquire the lock
        if lock_key:
            identifier = str(uuid.uuid4())
            result = await self.client.set(lock_key, identifier, nx=True, px=lock_timeout)
            if not result:
                raise Exception(f"Could not acquire lock for key {lock_key}")

        try:
            yield self.client
        except Exception as e:
            raise e
        finally:
            # release lock
            # lua script to do it without sequencing
            if lock_key and identifier:
                lua_script = """
                if redis.call("GET", KEYS[1]) == ARGV[1] then
                    return redis.call("DEL", KEYS[1])
                else
                    return 0
                end
                """
                await self.client.eval(lua_script, 1, lock_key, identifier)

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
