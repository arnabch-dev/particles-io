from typing import Annotated
import asyncio
from fastapi import APIRouter, Request, Header
from system.cache.cache import get_cache_from_request
from system.cache.players_lobby import PlayersLobby
from system.cache.players import PlayersCache
from system.socket.utils import dump_player_details
from system.events.publishers import player_joined
from system.auth import VerifyToken
from pydantic import BaseModel

router = APIRouter()


class HeaderPayload(BaseModel):
    token: str


@router.post("/")
async def add_to_lobby(request: Request, headers: Annotated[HeaderPayload, Header()]):
    cache = get_cache_from_request(request)
    lobby = PlayersLobby(cache)
    player_cache = PlayersCache(cache)
    verifier = VerifyToken()
    player_info = await verifier.verify(token=headers.token)
    player_id = player_info.get("sub")
    player_details = dump_player_details("", player_id, "")
    await asyncio.gather(
        lobby.add_player(player_id), player_cache.set_player(player_details)
    )
    await player_joined()
    return {"success": True}
