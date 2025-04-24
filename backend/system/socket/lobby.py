from socketio import AsyncNamespace
from system.cache.cache import Cache
from .decorators import con_event
from system.cache.players_lobby import PlayersLobbyCache
from system.events import pub_sub
from system.events.events import PLAYERS_JOINED
from .utils import dump_player_details


class LobbyNamespace(AsyncNamespace):
    def __init__(self, namespace="/lobby", app=None):
        super().__init__(namespace)
        self.app = app

    def set_app(self, app):
        self.app = app

    @con_event
    async def on_connect(self, sid, cache: Cache, user_id: str, *args, **kwargs):
        lobby_cache = PlayersLobbyCache(cache)
        player_in_lobby = await lobby_cache.has(user_id)
        if player_in_lobby:
            return
        player_details = dump_player_details(sid, user_id, "")
        await pub_sub.publish(PLAYERS_JOINED, player_details.model_dump_json())
