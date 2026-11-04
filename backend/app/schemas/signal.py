from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from app.core.constants import SignalPhase, SignalLamp, Direction


class VirtualSignalState(BaseModel):
    junction_id: str
    junction_code: str
    current_phase: SignalPhase
    phase_duration_seconds: int
    remaining_seconds: int
    elapsed_seconds: int
    north_south_lamp: SignalLamp
    east_west_lamp: SignalLamp
    priority_corridor: Direction
    priority_score_ns: float
    priority_score_ew: float
    disclaimer: str = "INFORMATIONAL ONLY - Do not override physical traffic lights"
    last_recalculated: datetime


class UserSignalAdvisory(BaseModel):
    junction_id: str
    corridor: Direction
    distance_meters: float
    user_signal_lamp: SignalLamp
    phase_remaining_seconds: int
    advisory_title: str
    advisory_message: str
    advisory_severity: str  # info | warning | alert
    action: str  # PROCEED | PREPARE_GREEN | HOLD | REROUTE
    detour_benefit: Optional[str] = None

