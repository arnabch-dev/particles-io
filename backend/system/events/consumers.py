from . import pub_sub
import json, asyncio
from redis import Redis
from system.cache.cache import Cache
from system.cache.players_lobby import PlayersLobbyCache
from system.cache.players import PlayersCache
from system.cache.available_rooms import AvailableRoomsCache
from system.cache.room import RoomCache
from system.cache.leaderboard import LeaderboardCache
from system.models import Player
from system.events.events import PLAYERS_JOINED, ROOM_OVER
from system.utils import get_random_object_id
from system.sio import sio
from system.db import DBSessionManager
from system.database.utils import add_room, add_players, get_players_of_room
from system.database.utils import mark_game_over
from system.socket.utils import dump_player_details

# TODO: write a consumer starter script to publish an event to the consumer for the lobby handling in case of failures if happend
# TODO: write a consumer starter script to get the room with scores


@pub_sub.pattern_subscribe(PLAYERS_JOINED)
async def add_player_to_room(data: dict, cache: Redis, cache_helper: Cache, db_session:DBSessionManager):
    print("event published")
    lobby_cache = PlayersLobbyCache(cache)
    players_cache = PlayersCache(cache)
    player = await players_cache.get_player(data.get("player_id"))
    if player and player.room_id:
        print("player having room ", player)
        return
    avaialbe_rooms = AvailableRoomsCache(cache)
    room = await avaialbe_rooms.get_room_with_most_player()
    room_id = ""
    if room:
        room_id, _ = room
    else:
        room_id = get_random_object_id()
    async with cache_helper.transaction_per_key(room_id) as _:
        score = await avaialbe_rooms.increment_room_score_till_threshold(room_id)
        room_cache = RoomCache(cache, room_id)
        await lobby_cache.remove_player(data.get("player_id"))
        await room_cache.add_player(data.get("player_id"))
        await players_cache.set_player(
            dump_player_details(
                data.get("sid"),
                data.get("player_id"),
                room_id,
                prev_color=data.get("color"),
            ),
        )
        # for the lobby namespace so that all the players can get the event of game start
        await sio.enter_room(data.get("sid"), room=room_id, namespace="/lobby")
        await sio.emit(
            "game:room-added",
            {"room_id": room_id},
            to=data.get("sid"),
            namespace="/lobby",
        )

        if score == -1:
            leaderboard = LeaderboardCache(cache,room_id)
            async with db_session.session() as session:
                players = []
                for player_id in await room_cache.get_all_players():
                    players.append(player_id)
                await add_room(session,room_id)
                await add_players(session,players,room_id)
                await session.commit()
            await asyncio.gather(
                room_cache.add_room(cache, room_id),
                leaderboard.init_leaderboard({player:0 for player in players})
            )
            await sio.emit(
                "game:start", {"room_id": room_id}, room=room_id, namespace="/lobby"
            )


@pub_sub.pattern_subscribe(ROOM_OVER)
async def complete_room(room_id: str, cache: Redis, cache_helper: Cache, db_session: DBSessionManager):
    # HACK: dont remove the leaderboard as it can be used as a cache to serve the users
    async with db_session.session() as session:
        players = await get_players_of_room(session, room_id)
        leaderboard = LeaderboardCache(cache, room_id)
        scores = {player.player_id: 0 for player in players}

        leaderboard_data = await leaderboard.get_leaderboard()

        for player_id,score in leaderboard_data.items():
            scores[player_id] = score

        scores_json = json.dumps(scores)

        await mark_game_over(session, room_id, scores_json),

        await session.commit()