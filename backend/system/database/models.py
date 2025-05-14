from system.db import Base
from sqlalchemy import (
    Column, String, Integer, DateTime,Enum, func, JSON
)
import enum

# using a basic model
# not creating rooms as such
# TODO: improve the modelling -> add another room model to store the metadata regarding the room, adding foreign keys

class RoomStatus(enum.Enum):
    started = "started"
    completed = "completed"

class Room(Base):
    __tablename__ = "room"
    id = Column(Integer,primary_key=True,autoincrement=True)
    room_id = Column(String(50),nullable=False)
    status = Column(Enum(RoomStatus), default=RoomStatus.started)
    created_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    leaderboard = Column(JSON,nullable=True,default=None)

class Player(Base):
    __tablename__ = "player"
    id = Column(Integer,primary_key=True,autoincrement=True)
    room_id = Column(String(50),nullable=False)
    player_id = Column(String(50),primary_key=True,nullable=False)
    # a color

class RoomHistory(Base):
    __tablename__ = "room_history"
    id = Column(Integer,primary_key=True,autoincrement=True)
    room_id = Column(String(50),nullable=False)
    player_id = Column(String(50),primary_key=True,nullable=False)
    score = Column(Integer,default=0)
    created_at = Column(DateTime, server_default=func.now())