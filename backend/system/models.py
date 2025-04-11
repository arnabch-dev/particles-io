from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class Player(BaseModel):
    sid: str
    player_id: str
    username: str
    color: str
    room_id: str
    ping_ms: Optional[float] = None  # Calculated latency
    last_sequence: Optional[int] = 0  # Last processed sequence number
    last_active: Optional[datetime] = None
    position: Optional[dict] = Field(default_factory=dict)  # e.g., {"x": 10, "y": 5}
    is_connected: bool = True


class PlayerResponse(BaseModel):
    player_id: str
    username: str
    color: str
    position: Optional[dict] = Field(default_factory=dict)


class Projectile(BaseModel):
    user_id: str
    position: dict
    angle: int | float
    # fired_at: datetime
    sequence_number: int = 0

class ProjectileResponse(Projectile):
    color: str

class Activity(BaseModel):
    player_id: str
    banned: bool = False
    ban_reason: Optional[str] = None
    ban_until: Optional[datetime] = None
    suspicious_count: int = 0


class RateLimit(BaseModel):
    player_id: str
    move_events: int = 0
    shoot_events: int = 0
    last_checked: datetime
    cooldown_until: Optional[datetime] = None
