from . import pub_sub
import json
from system.cache.cache import Cache
from system.cache.players_lobby import PlayersLobbyCache
from system.cache.players import PlayersCache
from system.cache.available_rooms import AvailableRoomsCache
from system.cache.room import RoomCache
from system.models import Player
from system.events.events import PLAYERS_JOINED,ROOM_READY
from system.utils import get_random_object_id
from system.sio import sio

@pub_sub.pattern_subscribe(PLAYERS_JOINED)
async def add_player_to_room(data:dict,cache:Cache):
    lobby_cache = PlayersLobbyCache(cache)
    players_cache = PlayersCache(cache)
    #TODO: need to have transaction and atomicity here
    player = await players_cache.get_player(data.get("player_id"))
    if player and player.room_id:
        return
    avaialbe_rooms = AvailableRoomsCache(cache)
    room = await avaialbe_rooms.get_room_with_most_player()
    room_id = ""
    if room:
        room_id,_ = room
    else:
        room_id = get_random_object_id()
    
    score = await avaialbe_rooms.increment_room_score_till_threshold(room_id)
    await lobby_cache.remove_player(player.player_id)
    if score == -1:
        # await pub_sub.publish(ROOM_READY,json.dumps({"room_id":room_id})) 
        # not doing publish rather sending all players ready as the player size are limited
        # we may want to set the state of the player in the cache if required
        # otherwise automatically the state will be refreshed once he joins the game namespace
        # TODO: updating state mechanism for metadata of room like started, playing,leaderboard settlement
        # TODO: adding player to the room
        # game_room_cache = RoomCache(cache,room_id=room_id)
        await sio.emit("game:start",room=room_id)
    
        return

    await sio.emit("game:room-added",{"room_id":room_id},to=player.sid,namespace="lobby")