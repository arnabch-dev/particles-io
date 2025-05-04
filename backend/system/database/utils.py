from sqlalchemy.ext.asyncio import AsyncSession
from system.database.models import RoomHistory, RoomStatus

async def add_room(db: AsyncSession, rooms: list[tuple[str, str]]):
    """
        rooms means (room_id, player_id)
    """
    new_rooms = [RoomHistory(room_id=room_id, player_id=player_id) for room_id, player_id in rooms]
    db.add_all(new_rooms)
    await db.flush()