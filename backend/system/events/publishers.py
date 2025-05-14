from . import pub_sub
from ..cache.players_lobby import PlayersLobbyCache
from ..models import Player
from .events import PLAYERS_JOINED,ROOM_OVER

async def publish_player_joined(player: Player):
    await pub_sub.publish(PLAYERS_JOINED, player.model_dump_json())

async def publish_game_over(room_id):
    await pub_sub.publish(ROOM_OVER,room_id)