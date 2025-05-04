from system.db import Base
from sqlalchemy import (
    Column, String, Integer, DateTime,Enum, func
)
import enum

# using a basic model
# not creating rooms as such
# TODO: improve the modelling -> add another room model to store the metadata regarding the room

class RoomStatus(enum.Enum):
    started = "started"
    completed = "completed"


class RoomHistory(Base):
    __tablename__ = "room_history"
    id = Column(Integer,primary_key=True,autoincrement=True)
    room_id = Column(String(50),nullable=False)
    player_id = Column(String(50),primary_key=True,nullable=False)
    score = Column(Integer,default=0)
    status = Column(Enum(RoomStatus), default=RoomStatus.started)
    created_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)

