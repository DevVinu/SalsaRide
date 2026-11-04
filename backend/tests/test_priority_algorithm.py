import pytest
from app.core.constants import Direction, SignalPhase, CongestionLevel
from app.schemas.traffic import CorridorTrafficSummary
from app.services.priority_algorithm import priority_calculator


def test_priority_algorithm_weighted_score():
    # Corridors: North has heavy traffic, others light
    summaries = {
        Direction.NORTH: CorridorTrafficSummary(
            direction=Direction.NORTH,
            vehicle_count=15,
            inner_zone_count=10,
            mid_zone_count=5,
            outer_zone_count=0,
            average_speed_kmh=8.0,
            average_wait_time_seconds=35.0,
            max_wait_time_seconds=45.0,
            congestion_level=CongestionLevel.OVERCROWDED,
            priority_score=0.0,
        ),
        Direction.SOUTH: CorridorTrafficSummary(
            direction=Direction.SOUTH,
            vehicle_count=10,
            inner_zone_count=6,
            mid_zone_count=4,
            outer_zone_count=0,
            average_speed_kmh=12.0,
            average_wait_time_seconds=20.0,
            max_wait_time_seconds=25.0,
            congestion_level=CongestionLevel.MODERATE,
            priority_score=0.0,
        ),
        Direction.EAST: CorridorTrafficSummary(
            direction=Direction.EAST,
            vehicle_count=2,
            inner_zone_count=1,
            mid_zone_count=1,
            outer_zone_count=0,
            average_speed_kmh=35.0,
            average_wait_time_seconds=5.0,
            max_wait_time_seconds=5.0,
            congestion_level=CongestionLevel.CLEAR,
            priority_score=0.0,
        ),
        Direction.WEST: CorridorTrafficSummary(
            direction=Direction.WEST,
            vehicle_count=3,
            inner_zone_count=2,
            mid_zone_count=1,
            outer_zone_count=0,
            average_speed_kmh=30.0,
            average_wait_time_seconds=6.0,
            max_wait_time_seconds=8.0,
            congestion_level=CongestionLevel.CLEAR,
            priority_score=0.0,
        ),
    }

    result = priority_calculator.evaluate_intersection_priorities(summaries)
    assert result["recommended_phase"] == SignalPhase.NORTH_SOUTH_GREEN
    assert result["score_ns"] > result["score_ew"]
    assert result["allocated_green_seconds"] > 10


def test_anti_starvation_fairness_rule():
    """
    Guarantees that an approach with low vehicle count but prolonged wait time
    (starvation >= 60s) receives forced priority over high-volume lanes.
    """
    summaries = {
        Direction.NORTH: CorridorTrafficSummary(
            direction=Direction.NORTH,
            vehicle_count=18,
            inner_zone_count=10,
            mid_zone_count=8,
            outer_zone_count=0,
            average_speed_kmh=10.0,
            average_wait_time_seconds=25.0,
            max_wait_time_seconds=30.0,  # High count but recent
            congestion_level=CongestionLevel.OVERCROWDED,
            priority_score=0.0,
        ),
        Direction.SOUTH: CorridorTrafficSummary(
            direction=Direction.SOUTH,
            vehicle_count=10,
            inner_zone_count=5,
            mid_zone_count=5,
            outer_zone_count=0,
            average_speed_kmh=15.0,
            average_wait_time_seconds=20.0,
            max_wait_time_seconds=25.0,
            congestion_level=CongestionLevel.MODERATE,
            priority_score=0.0,
        ),
        Direction.EAST: CorridorTrafficSummary(
            direction=Direction.EAST,
            vehicle_count=2,
            inner_zone_count=2,
            mid_zone_count=0,
            outer_zone_count=0,
            average_speed_kmh=0.0,
            average_wait_time_seconds=65.0,
            max_wait_time_seconds=70.0,  # STARVING! Waiting 70 seconds
            congestion_level=CongestionLevel.CLEAR,
            priority_score=0.0,
        ),
        Direction.WEST: CorridorTrafficSummary(
            direction=Direction.WEST,
            vehicle_count=1,
            inner_zone_count=1,
            mid_zone_count=0,
            outer_zone_count=0,
            average_speed_kmh=0.0,
            average_wait_time_seconds=60.0,
            max_wait_time_seconds=62.0,  # STARVING! Waiting 62 seconds
            congestion_level=CongestionLevel.CLEAR,
            priority_score=0.0,
        ),
    }

    result = priority_calculator.evaluate_intersection_priorities(summaries)
    assert result["starvation_active"] is True
    # Anti-starvation overrides North-South and assigns East-West green
    assert result["recommended_phase"] == SignalPhase.EAST_WEST_GREEN
    assert result["score_ew"] > result["score_ns"]


def test_emergency_vehicle_preemption():
    """An emergency vehicle (ambulance/fire) should override normal priorities."""
    summaries = {
        Direction.NORTH: CorridorTrafficSummary(
            direction=Direction.NORTH,
            vehicle_count=20,
            inner_zone_count=15,
            mid_zone_count=5,
            outer_zone_count=0,
            average_speed_kmh=5.0,
            average_wait_time_seconds=40.0,
            max_wait_time_seconds=45.0,
            congestion_level=CongestionLevel.OVERCROWDED,
            priority_score=0.0,
        ),
        Direction.SOUTH: CorridorTrafficSummary(
            direction=Direction.SOUTH,
            vehicle_count=15,
            inner_zone_count=10,
            mid_zone_count=5,
            outer_zone_count=0,
            average_speed_kmh=8.0,
            average_wait_time_seconds=30.0,
            max_wait_time_seconds=35.0,
            congestion_level=CongestionLevel.OVERCROWDED,
            priority_score=0.0,
        ),
        Direction.EAST: CorridorTrafficSummary(
            direction=Direction.EAST,
            vehicle_count=1,
            inner_zone_count=1,
            mid_zone_count=0,
            outer_zone_count=0,
            average_speed_kmh=0.0,
            average_wait_time_seconds=10.0,
            max_wait_time_seconds=10.0,
            congestion_level=CongestionLevel.CLEAR,
            priority_score=0.0,
            has_emergency=True,  # Ambulance approaching on East
        ),
        Direction.WEST: CorridorTrafficSummary(
            direction=Direction.WEST,
            vehicle_count=0,
            inner_zone_count=0,
            mid_zone_count=0,
            outer_zone_count=0,
            average_speed_kmh=45.0,
            average_wait_time_seconds=0.0,
            max_wait_time_seconds=0.0,
            congestion_level=CongestionLevel.CLEAR,
            priority_score=0.0,
        ),
    }

    result = priority_calculator.evaluate_intersection_priorities(summaries)
    assert result["emergency_preemption"] is True
    assert result["recommended_phase"] == SignalPhase.EAST_WEST_GREEN

