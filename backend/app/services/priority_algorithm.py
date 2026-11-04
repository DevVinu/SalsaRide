from typing import Dict, Tuple
from app.core.constants import Direction, SignalPhase, CongestionLevel
from app.schemas.traffic import CorridorTrafficSummary
from app.config import settings


class TrafficPriorityCalculator:
    """
    Intelligent Multi-Factor Weighted Priority Scoring with Anti-Starvation Fairness Rules.
    Guarantees low-volume cross-streets are never trapped in indefinite red signals.
    """

    def __init__(
        self,
        weight_count: float = 0.25,
        weight_density: float = 0.20,
        weight_avg_wait: float = 0.25,
        weight_max_wait: float = 0.15,
        weight_emergency: float = 0.15,
    ):
        self.w_count = weight_count
        self.w_density = weight_density
        self.w_avg_wait = weight_avg_wait
        self.w_max_wait = weight_max_wait
        self.w_emergency = weight_emergency

    def calculate_corridor_score(self, summary: CorridorTrafficSummary) -> Tuple[float, bool]:
        """
        Calculates priority score for a single corridor.
        Returns: (score, is_starving_flag)
        """
        # 1. Normalized vehicle count (scale 0 - 100, saturated at 20 vehicles)
        norm_count = min(100.0, (summary.vehicle_count / 20.0) * 100.0)

        # 2. Density factor (inner zone is weighted 2x because it represents the immediate bottleneck)
        density_val = min(100.0, ((summary.inner_zone_count * 2.0 + summary.mid_zone_count) / 25.0) * 100.0)

        # 3. Average wait time normalized (scale up to 60s)
        norm_avg_wait = min(100.0, (summary.average_wait_time_seconds / 60.0) * 100.0)

        # 4. Maximum wait time normalized (scale up to 75s)
        norm_max_wait = min(100.0, (summary.max_wait_time_seconds / 75.0) * 100.0)

        # 5. Emergency vehicle bonus
        emergency_val = 100.0 if summary.has_emergency else 0.0

        # Anti-Starvation Check:
        # If any commuter on this corridor has been waiting >= STARVATION_THRESHOLD_SECONDS,
        # flag as starving to trigger forced right-of-way
        is_starving = (
            summary.vehicle_count > 0
            and summary.max_wait_time_seconds >= settings.STARVATION_THRESHOLD_SECONDS
        )

        base_score = (
            self.w_count * norm_count
            + self.w_density * density_val
            + self.w_avg_wait * norm_avg_wait
            + self.w_max_wait * norm_max_wait
            + self.w_emergency * emergency_val
        )

        # Starvation multiplier boosts score to guarantee rotation
        if is_starving:
            base_score += 150.0

        # Emergency override puts score beyond any standard traffic count
        if summary.has_emergency:
            base_score += 300.0

        return round(base_score, 2), is_starving

    def evaluate_intersection_priorities(
        self, corridor_summaries: Dict[Direction, CorridorTrafficSummary]
    ) -> Dict[str, Any]:
        """
        Evaluates all corridors and groups compatible movements:
        North-South (NS) vs East-West (EW).
        Computes optimal phase and dynamic green duration.
        """
        scored_corridors: Dict[Direction, CorridorTrafficSummary] = {}
        highest_score = -1.0
        priority_direction = Direction.NORTH

        for direction, summary in corridor_summaries.items():
            score, is_starving = self.calculate_corridor_score(summary)
            updated = summary.model_copy(
                update={"priority_score": score, "is_starving": is_starving}
            )
            scored_corridors[direction] = updated

            if score > highest_score:
                highest_score = score
                priority_direction = direction

        # Group compatible movements:
        # Phase NS: North + South
        score_ns = scored_corridors[Direction.NORTH].priority_score + scored_corridors[Direction.SOUTH].priority_score
        # Phase EW: East + West
        score_ew = scored_corridors[Direction.EAST].priority_score + scored_corridors[Direction.WEST].priority_score

        # Determine recommended phase
        if score_ew > score_ns:
            recommended_phase = SignalPhase.EAST_WEST_GREEN
            active_score = score_ew
            opposing_score = score_ns
        else:
            recommended_phase = SignalPhase.NORTH_SOUTH_GREEN
            active_score = score_ns
            opposing_score = score_ew

        # Dynamic Green duration allocation:
        # Range: [MIN_GREEN_DURATION, MAX_GREEN_DURATION]
        total_score = active_score + opposing_score
        if total_score > 0:
            ratio = active_score / total_score
            allocated_green = round(
                settings.MIN_GREEN_DURATION
                + ratio * (settings.MAX_GREEN_DURATION - settings.MIN_GREEN_DURATION)
            )
        else:
            allocated_green = settings.MIN_GREEN_DURATION

        allocated_green = max(
            settings.MIN_GREEN_DURATION,
            min(settings.MAX_GREEN_DURATION, allocated_green),
        )

        return {
            "corridors": scored_corridors,
            "priority_direction": priority_direction,
            "recommended_phase": recommended_phase,
            "score_ns": round(score_ns, 2),
            "score_ew": round(score_ew, 2),
            "allocated_green_seconds": allocated_green,
            "starvation_active": any(c.is_starving for c in scored_corridors.values()),
            "emergency_preemption": any(c.has_emergency for c in scored_corridors.values()),
        }


from typing import Any
priority_calculator = TrafficPriorityCalculator()

