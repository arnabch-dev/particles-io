from sqlalchemy.ext.asyncio import AsyncSession
from system.database.models import RoomHistory, RoomStatus, Room,Player

async def add_players(db: AsyncSession, players, room_id):
    """
        rooms means (room_id, player_id)
    """
    new_players = [Player(room_id=room_id, player_id=player_id) for player_id in players]
    db.add_all(new_players)
    await db.flush()

async def add_room(db:AsyncSession,room_id):
    db.add(Room(room_id=room_id))
    await db.flush()