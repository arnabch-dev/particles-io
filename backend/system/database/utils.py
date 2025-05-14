from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from system.database.models import RoomStatus, Room,Player

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


async def mark_game_over(session: AsyncSession, room_id: str,leaderboard):
    stmt = select(Room).where(Room.room_id == room_id)
    result = await session.execute(stmt)
    room = result.scalar_one_or_none()

    if room:
        room.status = RoomStatus.completed
        room.closed_at = func.now()
        room.leaderboard = leaderboard

async def get_players_of_room(session:AsyncSession,room_id:str):
    stmt = select(Player).where(room_id == room_id)
    result = await session.execute(stmt)
    players = result.scalars().all()
    return players

async def get_leaderboard_of_room(session:AsyncSession,room_id:str):
    stmt = select(Room).where(Room.room_id == room_id)
    result = await session.execute(stmt)
    room = result.scalar_one_or_none()
    if not room:
        return room
    return room.leaderboard