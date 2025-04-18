from typing import Annotated
from fastapi import APIRouter, Request, Header
from system.cache.cache import get_cache_from_request
from system.cache.players_lobby import PlayersLobby
from system.auth import VerifyToken
from pydantic import BaseModel
router = APIRouter()

class HeaderPayload(BaseModel):
    token:str

@router.post("/")
async def add_to_lobby(request:Request,headers: Annotated[HeaderPayload,Header()]):
    cache = get_cache_from_request(request)
    lobby = PlayersLobby(cache)
    verifier = VerifyToken()
    player_info = await verifier.verify(token=headers.token)
    player_id = player_info.get("sub")
    await lobby.add_player(player_id)