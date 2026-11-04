import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.core.constants import Direction, CongestionLevel
from app.schemas.traffic import CorridorTrafficSummary, JunctionTrafficStatus
from app.services.geo_service import (
    calculate_haversine_distance,
    determine_corridor_approach,
    classify_detection_zone,
)
from app.database import db_manager


class ParticipantObservation:
    def __init__(
        self,
        user_id: str,
        junction_id: str,
        corridor: Direction,
        distance_meters: float,
        speed_kmh: float,
        is_emergency: bool = False,
        first_seen_time: Optional[float] = None,
    ):
        self.user_id = user_id
        self.junction_id = junction_id
        self.corridor = corridor
        self.distance_meters = distance_meters
        self.speed_kmh = speed_kmh
        self.is_emergency = is_emergency
        self.first_seen_time = first_seen_time or time.time()
        self.last_ping_time = time.time()

    @property
    def waiting_time_seconds(self) -> float:
        # If stopped or crawling (< 5 km/h) in inner/mid zone, accumulate wait time
        if self.speed_kmh < 10.0:
            return round(time.time() - self.first_seen_time, 1)
        return 0.0


class TrafficService:
    def __init__(self):
        # junction_id -> list of ParticipantObservation
        self._active_participants: Dict[str, Dict[str, ParticipantObservation]] = {}

    def record_user_ping(
        self,
        user_id: str,
        junction: Dict[str, Any],
        user_lat: float,
        user_lon: float,
        speed_kmh: float = 0.0,
        is_emergency: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Processes an inbound location ping.
        If inside the detection radius, updates or creates active observation.
        If outside detection radius, ensures participant is de-registered.
        """
        junction_id = str(junction.get("id") or junction.get("_id") or junction.get("junction_code"))
        j_lat = float(junction["latitude"])
        j_lon = float(junction["longitude"])
        radius = float(junction.get("detection_radius_meters", 500))

        dist = calculate_haversine_distance(user_lat, user_lon, j_lat, j_lon)

        if junction_id not in self._active_participants:
            self._active_participants[junction_id] = {}

        if dist > radius:
            # Participant has left the detection zone
            if user_id in self._active_participants[junction_id]:
                del self._active_participants[junction_id][user_id]
            return None

        # Inside detection zone: determine corridor and zone
        corridor = determine_corridor_approach(user_lat, user_lon, j_lat, j_lon)
        zone = classify_detection_zone(
            dist,
            inner_radius=junction.get("inner_zone_meters", 150),
            mid_radius=junction.get("mid_zone_meters", 300),
            outer_radius=radius,
        )

        existing = self._active_participants[junction_id].get(user_id)
        if existing:
            existing.corridor = corridor
            existing.distance_meters = dist
            existing.speed_kmh = speed_kmh
            existing.is_emergency = is_emergency
            existing.last_ping_time = time.time()
        else:
            self._active_participants[junction_id][user_id] = ParticipantObservation(
                user_id=user_id,
                junction_id=junction_id,
                corridor=corridor,
                distance_meters=dist,
                speed_kmh=speed_kmh,
                is_emergency=is_emergency,
            )

        return {
            "user_id": user_id,
            "junction_id": junction_id,
            "corridor": corridor,
            "distance_meters": dist,
            "zone": zone,
            "speed_kmh": speed_kmh,
            "is_emergency": is_emergency,
            "waiting_time_seconds": self._active_participants[junction_id][user_id].waiting_time_seconds,
        }

    def prune_stale_participants(self, max_idle_seconds: float = 60.0):
        """Removes participants that haven't sent a location ping recently."""
        now = time.time()
        for j_id in list(self._active_participants.keys()):
            participants = self._active_participants[j_id]
            stale_keys = [
                uid
                for uid, obs in participants.items()
                if (now - obs.last_ping_time) > max_idle_seconds
            ]
            for uid in stale_keys:
                del participants[uid]

    def get_corridor_summaries(self, junction_id: str) -> Dict[Direction, CorridorTrafficSummary]:
        self.prune_stale_participants()
        participants = list(self._active_participants.get(junction_id, {}).values())

        summaries: Dict[Direction, CorridorTrafficSummary] = {}

        for direction in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
            corridor_users = [p for p in participants if p.corridor == direction]
            count = len(corridor_users)

            inner_count = sum(1 for p in corridor_users if p.distance_meters <= 150.0)
            mid_count = sum(1 for p in corridor_users if 150.0 < p.distance_meters <= 300.0)
            outer_count = sum(1 for p in corridor_users if p.distance_meters > 300.0)

            avg_speed = (
                round(sum(p.speed_kmh for p in corridor_users) / count, 1)
                if count > 0
                else 45.0
            )

            wait_times = [p.waiting_time_seconds for p in corridor_users]
            avg_wait = round(sum(wait_times) / count, 1) if count > 0 else 0.0
            max_wait = round(max(wait_times), 1) if count > 0 else 0.0
            has_sos = any(p.is_emergency for p in corridor_users)

            # Classify congestion
            if count >= 10 or (count >= 5 and avg_speed < 12.0):
                congestion = CongestionLevel.OVERCROWDED
            elif count >= 4:
                congestion = CongestionLevel.MODERATE
            else:
                congestion = CongestionLevel.CLEAR

            summaries[direction] = CorridorTrafficSummary(
                direction=direction,
                vehicle_count=count,
                inner_zone_count=inner_count,
                mid_zone_count=mid_count,
                outer_zone_count=outer_count,
                average_speed_kmh=avg_speed,
                average_wait_time_seconds=avg_wait,
                max_wait_time_seconds=max_wait,
                congestion_level=congestion,
                priority_score=0.0,
                is_starving=False,
                has_emergency=has_sos,
            )

        return summaries

    def get_active_participants_list(self, junction_id: str) -> List[Dict[str, Any]]:
        participants = self._active_participants.get(junction_id, {})
        return [
            {
                "user_id": obs.user_id,
                "corridor": obs.corridor.value,
                "distance_meters": obs.distance_meters,
                "speed_kmh": obs.speed_kmh,
                "waiting_time_seconds": obs.waiting_time_seconds,
                "is_emergency": obs.is_emergency,
            }
            for obs in participants.values()
        ]

    def clear_junction_participants(self, junction_id: str):
        if junction_id in self._active_participants:
            self._active_participants[junction_id].clear()


traffic_service = TrafficService()

