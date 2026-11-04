from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.constants import Direction, CongestionLevel


class LocationPing(BaseModel):
    user_id: Optional[str] = None
    latitude: float
    longitude: float
    speed_kmh: float = 0.0
    accuracy_meters: Optional[float] = None
    heading_degrees: Optional[float] = None
    is_emergency: bool = False


class CorridorTrafficSummary(BaseModel):
    direction: Direction
    vehicle_count: int
    inner_zone_count: int
    mid_zone_count: int
    outer_zone_count: int
    average_speed_kmh: float
    average_wait_time_seconds: float
    max_wait_time_seconds: float
    congestion_level: CongestionLevel
    priority_score: float
    is_starving: bool = False
    has_emergency: bool = False


class JunctionTrafficStatus(BaseModel):
    junction_id: str
    junction_code: str
    name: str
    total_participating_vehicles: int
    corridors: Dict[str, CorridorTrafficSummary]
    last_updated: datetime


class SimulatedVehicleInject(BaseModel):
    corridor: Direction
    speed_kmh: float = 25.0
    distance_fraction: float = Field(0.5, ge=0.05, le=0.95, description="0.1 = close to light, 0.9 = outer zone")
    is_emergency: bool = False
    waiting_seconds: float = 0.0

