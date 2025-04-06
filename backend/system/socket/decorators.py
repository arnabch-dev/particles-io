from functools import wraps
from system.auth import decode_access_token
from redis import Redis

def con_event(handler):
    """
        flow with the socket io event
        event(connect) => wrapper(*args, **kwargs)
        sio.event(wrapper) => registers handler for socket.io
    """
    @wraps(handler)
    async def wrapper(sid,environ,auth,*args,**kwargs):
        scope = environ.get("asgi.scope")
        app = scope.get("app")
        cache: Redis = app.state.cache.client
        headers = dict(scope.get("headers", []))
        # TODO: enable token verificaton
        # TODO: replace token with the decoded token
        # user_id = decode_access_token(token=auth.get("token"))
        # if not token:
        #     raise ConnectionRefusedError("No token present")
        user_id = auth.get("token")
        return await handler(
            sid,
            environ=environ,
            user_id = user_id,
            auth=auth,
            cache=cache,
            headers=headers,
            scope=scope,
            app=app,
            *args,
            **kwargs
        )

    return wrapper