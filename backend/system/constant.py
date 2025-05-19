import enum
MAX_MEMBERS = 2
class RoomStatus(enum.Enum):
    started = "started"
    completed = "completed"
    idle = "idle"
