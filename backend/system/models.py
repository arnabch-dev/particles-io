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
    velocity: Optional[dict] = Field(default_factory=dict)  # e.g., {"vx": 0, "vy": 0}
    is_connected: bool = True


class Projectile(BaseModel):
    projectile_id: str
    owner_id: str
    # start_position: dict  # {"x": float, "y": float}
    direction: dict  # {"x": float, "y": float} — normalized vector
    speed: float
    fired_at: datetime
    sequence_number: int


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
