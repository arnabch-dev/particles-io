import asyncio
import inspect
from redis.exceptions import ConnectionError
from system.cache.cache import Cache, serialise_cache_get_data


# A non blocking pubsub
class PubSub:
    def __init__(self):
        self._handlers = {}
        self._client = None
        self._pubsub = None

    def set_pubsub(self, cache: Cache):
        self._client = cache.client
        self._pubsub = self._client.pubsub()

    def subscribe(self, event: str):
        def decorator(func):
            self._handlers[("sub", event)] = func
            return func

        return decorator

    def pattern_subscribe(self, pattern: str):
        def decorator(func):
            self._handlers[("psub", pattern)] = func
            return func

        return decorator

    async def publish(self, event: str, payload: str):
        await self._client.publish(event, payload)

    async def start_listening(self):
        for mode, event in self._handlers:
            if mode == "sub":
                await self._pubsub.subscribe(event)
            elif mode == "psub":
                await self._pubsub.psubscribe(event)

        asyncio.create_task(self._listener())

    async def _listener(self):
        try:
            async for message in self._pubsub.listen():
                if message["type"] not in {"message", "pmessage"}:
                    continue

                if message["type"] == "message":
                    key = message["channel"].decode("utf-8")
                    handler = self._handlers.get(("sub", key))
                elif message["type"] == "pmessage":
                    key = message["pattern"].decode("utf-8")
                    handler = self._handlers.get(("psub", key))
                else:
                    handler = None
                try:
                    data = serialise_cache_get_data(message["data"])
                except Exception as e:
                    data = message["data"].decode("utf-8")

                if handler:
                    if inspect.iscoroutinefunction(handler):
                        await handler(data,cache=self._client)
                    else:
                        handler(data,cache=self._client)
        except ConnectionError as e:
            print("pubsub closed")

    async def close(self):
        await self._pubsub.close()
