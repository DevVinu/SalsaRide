from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class JunctionBase(BaseModel):
    junction_code: str
    name: str
    city: str
    address: str
    latitude: float
    longitude: float
    detection_radius_meters: int = 500
    inner_zone_meters: int = 150
    mid_zone_meters: int = 300
    is_active: bool = True


class JunctionCreate(JunctionBase):
    pass


class JunctionUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    detection_radius_meters: Optional[int] = None
    inner_zone_meters: Optional[int] = None
    mid_zone_meters: Optional[int] = None
    is_active: Optional[bool] = None


class JunctionResponse(JunctionBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

