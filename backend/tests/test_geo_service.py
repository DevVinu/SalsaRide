import pytest
from app.services.geo_service import (
    calculate_haversine_distance,
    calculate_bearing,
    determine_corridor_approach,
    classify_detection_zone,
)
from app.core.constants import Direction


def test_haversine_distance():
    # Distance between two known points in NYC (~1.1 km)
    # Grand Central (40.7527, -73.9772) and Times Square (40.7580, -73.9855)
    dist = calculate_haversine_distance(40.7527, -73.9772, 40.7580, -73.9855)
    assert 900 < dist < 1300, f"Expected ~1100m, got {dist}m"


def test_corridor_approach_classification():
    junction_lat, junction_lon = 40.7516, -73.9767

    # User positioned directly North
    user_north_lat = junction_lat + 0.003
    user_north_lon = junction_lon
    corridor_n = determine_corridor_approach(user_north_lat, user_north_lon, junction_lat, junction_lon)
    assert corridor_n == Direction.NORTH

    # User positioned directly East
    user_east_lat = junction_lat
    user_east_lon = junction_lon + 0.003
    corridor_e = determine_corridor_approach(user_east_lat, user_east_lon, junction_lat, junction_lon)
    assert corridor_e == Direction.EAST

    # User positioned directly South
    user_south_lat = junction_lat - 0.003
    user_south_lon = junction_lon
    corridor_s = determine_corridor_approach(user_south_lat, user_south_lon, junction_lat, junction_lon)
    assert corridor_s == Direction.SOUTH

    # User positioned directly West
    user_west_lat = junction_lat
    user_west_lon = junction_lon - 0.003
    corridor_w = determine_corridor_approach(user_west_lat, user_west_lon, junction_lat, junction_lon)
    assert corridor_w == Direction.WEST


def test_zone_classification():
    assert classify_detection_zone(80.0) == "INNER"
    assert classify_detection_zone(220.0) == "MID"
    assert classify_detection_zone(420.0) == "OUTER"
    assert classify_detection_zone(550.0) == "OUT_OF_ZONE"

