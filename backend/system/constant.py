import enum
MAX_MEMBERS = 3
class RoomStatus(enum.Enum):
    started = "started"
    completed = "completed"
    idle = "idle"
