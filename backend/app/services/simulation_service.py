import math
import random
import time
from typing import Dict, Any, List
from app.core.constants import Direction
from app.services.traffic_service import traffic_service


class SimulationService:
    def inject_simulated_vehicle(
        self,
        junction: Dict[str, Any],
        corridor: Direction,
        distance_fraction: float = 0.5,
        speed_kmh: float = 25.0,
        is_emergency: bool = False,
        waiting_seconds: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculates synthetic GPS coordinates along the specified approach corridor
        and registers the vehicle with traffic_service.
        """
        j_id = str(junction.get("id") or junction.get("_id") or junction.get("junction_code"))
        j_lat = float(junction["latitude"])
        j_lon = float(junction["longitude"])
        radius = float(junction.get("detection_radius_meters", 500))

        dist = max(30.0, min(radius - 20.0, distance_fraction * radius))

        # Offsets based on corridor
        angle_map = {
            Direction.NORTH: 0.0,
            Direction.EAST: 90.0,
            Direction.SOUTH: 180.0,
            Direction.WEST: 270.0,
        }
        angle_deg = angle_map[corridor] + (random.random() - 0.5) * 8.0
        rad = math.radians(angle_deg)

        # Approximate coordinate displacement
        delta_lat = (math.cos(rad) * dist) / 111000.0
        delta_lon = (math.sin(rad) * dist) / (111000.0 * math.cos(math.radians(j_lat)))

        user_lat = j_lat + delta_lat
        user_lon = j_lon + delta_lon

        veh_id = f"SIM-{corridor.value[:1]}-{random.randint(1000, 9999)}"
        if is_emergency:
            veh_id = f"EMG-SOS-{random.randint(100, 999)}"

        res = traffic_service.record_user_ping(
            user_id=veh_id,
            junction=junction,
            user_lat=user_lat,
            user_lon=user_lon,
            speed_kmh=speed_kmh,
            is_emergency=is_emergency,
        )

        # Backdate first seen time if waiting_seconds specified
        if res and waiting_seconds > 0:
            obs = traffic_service._active_participants[j_id].get(veh_id)
            if obs:
                obs.first_seen_time = time.time() - waiting_seconds

        return {
            "vehicle_id": veh_id,
            "corridor": corridor.value,
            "distance_meters": dist,
            "latitude": user_lat,
            "longitude": user_lon,
            "speed_kmh": speed_kmh,
            "is_emergency": is_emergency,
            "waiting_seconds": waiting_seconds,
        }

    def apply_scenario_preset(
        self, junction: Dict[str, Any], preset_name: str
    ) -> Dict[str, Any]:
        """Clears existing traffic and spawns a preset distribution."""
        j_id = str(junction.get("id") or junction.get("_id") or junction.get("junction_code"))
        traffic_service.clear_junction_participants(j_id)

        counts = {
            "morning_rush": {Direction.NORTH: 14, Direction.SOUTH: 12, Direction.EAST: 3, Direction.WEST: 2},
            "evening_rush": {Direction.NORTH: 4, Direction.SOUTH: 3, Direction.EAST: 15, Direction.WEST: 16},
            "bottleneck": {Direction.NORTH: 18, Direction.SOUTH: 4, Direction.EAST: 2, Direction.WEST: 2},
            "balanced": {Direction.NORTH: 6, Direction.SOUTH: 6, Direction.EAST: 5, Direction.WEST: 5},
            "emergency": {Direction.NORTH: 8, Direction.SOUTH: 6, Direction.EAST: 10, Direction.WEST: 4},
        }.get(preset_name, {Direction.NORTH: 8, Direction.SOUTH: 6, Direction.EAST: 4, Direction.WEST: 3})

        injected = []
        for corridor, count in counts.items():
            for i in range(count):
                frac = 0.15 + (i / max(1, count)) * 0.75
                is_sos = (preset_name == "emergency" and corridor == Direction.EAST and i == 0)
                speed = 6.0 if (frac < 0.35 and count > 8) else 28.0
                wait = 45.0 if (frac < 0.35 and count > 8) else 5.0
                item = self.inject_simulated_vehicle(
                    junction=junction,
                    corridor=corridor,
                    distance_fraction=frac,
                    speed_kmh=speed,
                    is_emergency=is_sos,
                    waiting_seconds=wait,
                )
                injected.append(item)

        return {
            "junction_id": j_id,
            "preset_applied": preset_name,
            "total_vehicles_injected": len(injected),
            "distribution": {c.value: counts[c] for c in counts},
        }


simulation_service = SimulationService()

