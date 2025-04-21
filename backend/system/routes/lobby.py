from typing import Annotated
import asyncio
from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from system.cache.cache import get_cache_from_request
from system.cache.players_lobby import PlayersLobbyCache
from system.cache.players import PlayersCache
from system.socket.utils import dump_player_details
from system.events.publishers import publish_player_joined
from system.auth import VerifyToken
from pydantic import BaseModel

router = APIRouter()


class HeaderPayload(BaseModel):
    token: str


@router.post("/")
async def add_to_lobby(request: Request, headers: Annotated[HeaderPayload, Header()]):
    cache = get_cache_from_request(request)
    lobby = PlayersLobbyCache(cache)
    player_cache = PlayersCache(cache)
    verifier = VerifyToken()
    player_info = await verifier.verify(token=headers.token)
    player_id = player_info.get("sub")
    existing_player = await player_cache.get_player(player_id)
    if existing_player:
        if existing_player.room_id:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "player already in a match",
                    "room": existing_player.room_id,
                },
            )
        player_details = dump_player_details(existing_player.sid, player_id, "")
        await player_cache.set_player(player_details)
        return {"success": True}

    # already in lobby
    if await lobby.has(player_id):
        return {"success": True}

    # else add to a queue
    player_details = dump_player_details("", player_id, "")
    await asyncio.gather(
        lobby.add_player(player_id), player_cache.set_player(player_details)
    )
    await publish_player_joined(player_details)
    return {"success": True}
