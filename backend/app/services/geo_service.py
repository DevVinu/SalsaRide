import math
from typing import Tuple, Optional, List, Dict, Any
from app.core.constants import Direction


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculates the great-circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


def calculate_bearing(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculates compass bearing from point1 to point2 in degrees (0 - 360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    diff_lambda = math.radians(lon2 - lon1)

    y = math.sin(diff_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - (
        math.sin(phi1) * math.cos(phi2) * math.cos(diff_lambda)
    )

    initial_bearing = math.degrees(math.atan2(y, x))
    return (initial_bearing + 360.0) % 360.0


def determine_corridor_approach(
    user_lat: float, user_lon: float, junction_lat: float, junction_lon: float
) -> Direction:
    """
    Determines approach corridor relative to junction center based on user bearing.
    Bearing from junction towards user:
      North approach: user is North of junction (bearing ~ 315 to 45 deg)
      East approach: user is East of junction (bearing ~ 45 to 135 deg)
      South approach: user is South of junction (bearing ~ 135 to 225 deg)
      West approach: user is West of junction (bearing ~ 225 to 315 deg)
    """
    bearing = calculate_bearing(junction_lat, junction_lon, user_lat, user_lon)

    if bearing >= 315.0 or bearing < 45.0:
        return Direction.NORTH
    elif 45.0 <= bearing < 135.0:
        return Direction.EAST
    elif 135.0 <= bearing < 225.0:
        return Direction.SOUTH
    else:
        return Direction.WEST


def classify_detection_zone(
    distance_meters: float,
    inner_radius: float = 150.0,
    mid_radius: float = 300.0,
    outer_radius: float = 500.0,
) -> str:
    """Classifies user proximity into INNER (stop-line), MID (slowdown), OUTER (catchment), or OUT_OF_ZONE."""
    if distance_meters <= inner_radius:
        return "INNER"
    elif distance_meters <= mid_radius:
        return "MID"
    elif distance_meters <= outer_radius:
        return "OUTER"
    else:
        return "OUT_OF_ZONE"

