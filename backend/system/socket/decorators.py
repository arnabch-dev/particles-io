from functools import wraps
from system.auth import VerifyToken
from redis import Redis
from system.cache.cache import get_cache_from_app

def con_event(handler):
    """
    flow with the socket io event
    event(connect) => wrapper(*args, **kwargs)
    sio.event(wrapper) => registers handler for socket.io
    """

    @wraps(handler)
    async def wrapper(*args, **kwargs):
        self,sid, environ, auth = args
        scope = environ.get("asgi.scope")
        app = scope.get("app")
        cache = get_cache_from_app(app)
        headers = dict(scope.get("headers", []))
        # TODO: enable token verificaton
        # TODO: replace token with the decoded token
        # user_id = decode_access_token(token=auth.get("token"))
        # if not token:
        #     raise ConnectionRefusedError("No token present")
        authorisation = VerifyToken()
        token = auth.get("token")
        user_auth_data = await authorisation.verify(token)
        user_id = user_auth_data.get("sub")
        return await handler(
            self,
            sid=sid,
            cache=cache,
            user_id=user_id,
            auth=auth,
            headers=headers,
            scope=scope,
            app=app,
        )

    return wrapper
