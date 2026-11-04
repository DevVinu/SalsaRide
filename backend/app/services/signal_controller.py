import time
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.constants import SignalPhase, SignalLamp, Direction
from app.schemas.signal import VirtualSignalState, UserSignalAdvisory
from app.config import settings
from app.services.traffic_service import traffic_service
from app.services.priority_algorithm import priority_calculator


class JunctionSignalStateMachine:
    def __init__(self, junction_id: str, junction_code: str):
        self.junction_id = junction_id
        self.junction_code = junction_code

        self.current_phase: SignalPhase = SignalPhase.NORTH_SOUTH_GREEN
        self.phase_duration_seconds: int = 24
        self.phase_started_at: float = time.time()
        self.priority_direction: Direction = Direction.NORTH
        self.score_ns: float = 0.0
        self.score_ew: float = 0.0

    @property
    def elapsed_seconds(self) -> int:
        return int(time.time() - self.phase_started_at)

    @property
    def remaining_seconds(self) -> int:
        rem = self.phase_duration_seconds - self.elapsed_seconds
        return max(0, rem)

    def get_lamp_states(self) -> tuple[SignalLamp, SignalLamp]:
        """Returns: (NS_Lamp, EW_Lamp)"""
        if self.current_phase == SignalPhase.NORTH_SOUTH_GREEN:
            return SignalLamp.GREEN, SignalLamp.RED
        elif self.current_phase == SignalPhase.NORTH_SOUTH_YELLOW:
            return SignalLamp.YELLOW, SignalLamp.RED
        elif self.current_phase in (
            SignalPhase.ALL_RED_TRANSITION_1,
            SignalPhase.ALL_RED_TRANSITION_2,
        ):
            return SignalLamp.RED, SignalLamp.RED
        elif self.current_phase == SignalPhase.EAST_WEST_GREEN:
            return SignalLamp.RED, SignalLamp.GREEN
        elif self.current_phase == SignalPhase.EAST_WEST_YELLOW:
            return SignalLamp.RED, SignalLamp.YELLOW
        return SignalLamp.RED, SignalLamp.RED

    def update_tick(self) -> bool:
        """
        Advances signal timer. Recalculates state and transitions phases when expired.
        Returns True if phase changed.
        """
        now = time.time()
        summaries = traffic_service.get_corridor_summaries(self.junction_id)
        eval_result = priority_calculator.evaluate_intersection_priorities(summaries)

        self.score_ns = eval_result["score_ns"]
        self.score_ew = eval_result["score_ew"]
        self.priority_direction = eval_result["priority_direction"]

        # Check Early-Cutoff & Emergency Preemption:
        is_ns_green = self.current_phase == SignalPhase.NORTH_SOUTH_GREEN
        is_ew_green = self.current_phase == SignalPhase.EAST_WEST_GREEN

        if (is_ns_green or is_ew_green) and self.remaining_seconds > 4:
            active_count = (
                summaries[Direction.NORTH].vehicle_count + summaries[Direction.SOUTH].vehicle_count
                if is_ns_green
                else summaries[Direction.EAST].vehicle_count + summaries[Direction.WEST].vehicle_count
            )
            opposing_count = (
                summaries[Direction.EAST].vehicle_count + summaries[Direction.WEST].vehicle_count
                if is_ns_green
                else summaries[Direction.NORTH].vehicle_count + summaries[Direction.SOUTH].vehicle_count
            )
            opposing_sos = (
                summaries[Direction.EAST].has_emergency or summaries[Direction.WEST].has_emergency
                if is_ns_green
                else summaries[Direction.NORTH].has_emergency or summaries[Direction.SOUTH].has_emergency
            )

            # Early Cutoff: Active queue empty while opposing has traffic OR opposing emergency
            if (active_count == 0 and opposing_count > 0) or opposing_sos:
                # Force immediate expiration
                self.phase_duration_seconds = self.elapsed_seconds

        # Check phase expiration
        if self.remaining_seconds <= 0:
            self._transition_next_phase(eval_result)
            return True

        return False

    def _transition_next_phase(self, eval_result: Dict[str, Any]):
        now = time.time()
        self.phase_started_at = now

        if self.current_phase == SignalPhase.NORTH_SOUTH_GREEN:
            self.current_phase = SignalPhase.NORTH_SOUTH_YELLOW
            self.phase_duration_seconds = settings.YELLOW_DURATION

        elif self.current_phase == SignalPhase.NORTH_SOUTH_YELLOW:
            self.current_phase = SignalPhase.ALL_RED_TRANSITION_1
            self.phase_duration_seconds = settings.ALL_RED_DURATION

        elif self.current_phase == SignalPhase.ALL_RED_TRANSITION_1:
            self.current_phase = SignalPhase.EAST_WEST_GREEN
            self.phase_duration_seconds = eval_result["allocated_green_seconds"]

        elif self.current_phase == SignalPhase.EAST_WEST_GREEN:
            self.current_phase = SignalPhase.EAST_WEST_YELLOW
            self.phase_duration_seconds = settings.YELLOW_DURATION

        elif self.current_phase == SignalPhase.EAST_WEST_YELLOW:
            self.current_phase = SignalPhase.ALL_RED_TRANSITION_2
            self.phase_duration_seconds = settings.ALL_RED_DURATION

        elif self.current_phase == SignalPhase.ALL_RED_TRANSITION_2:
            self.current_phase = SignalPhase.NORTH_SOUTH_GREEN
            self.phase_duration_seconds = eval_result["allocated_green_seconds"]

    def to_schema(self) -> VirtualSignalState:
        ns_lamp, ew_lamp = self.get_lamp_states()
        return VirtualSignalState(
            junction_id=self.junction_id,
            junction_code=self.junction_code,
            current_phase=self.current_phase,
            phase_duration_seconds=self.phase_duration_seconds,
            remaining_seconds=self.remaining_seconds,
            elapsed_seconds=self.elapsed_seconds,
            north_south_lamp=ns_lamp,
            east_west_lamp=ew_lamp,
            priority_corridor=self.priority_direction,
            priority_score_ns=self.score_ns,
            priority_score_ew=self.score_ew,
            last_recalculated=datetime.utcnow(),
        )

    def generate_advisory_for_user(
        self, corridor: Direction, distance_meters: float
    ) -> UserSignalAdvisory:
        ns_lamp, ew_lamp = self.get_lamp_states()
        is_ns = corridor in (Direction.NORTH, Direction.SOUTH)
        user_lamp = ns_lamp if is_ns else ew_lamp

        summaries = traffic_service.get_corridor_summaries(self.junction_id)
        corridor_sum = summaries[corridor]
        is_overcrowded = corridor_sum.congestion_level.value == "OVERCROWDED"

        if user_lamp == SignalLamp.GREEN:
            return UserSignalAdvisory(
                junction_id=self.junction_id,
                corridor=corridor,
                distance_meters=distance_meters,
                user_signal_lamp=user_lamp,
                phase_remaining_seconds=self.remaining_seconds,
                advisory_title="Priority Green Wave Active",
                advisory_message=f"Virtual Green allocated ({self.remaining_seconds}s remaining). Proceed safely through junction.",
                advisory_severity="info",
                action="PROCEED",
            )
        elif user_lamp == SignalLamp.YELLOW:
            return UserSignalAdvisory(
                junction_id=self.junction_id,
                corridor=corridor,
                distance_meters=distance_meters,
                user_signal_lamp=user_lamp,
                phase_remaining_seconds=self.remaining_seconds,
                advisory_title="Signal Clearing (Amber)",
                advisory_message="Virtual yellow clearing phase. Prepare to decelerate.",
                advisory_severity="warning",
                action="HOLD",
            )
        else:
            # User facing Red signal
            if is_overcrowded and distance_meters > 180.0:
                return UserSignalAdvisory(
                    junction_id=self.junction_id,
                    corridor=corridor,
                    distance_meters=distance_meters,
                    user_signal_lamp=user_lamp,
                    phase_remaining_seconds=self.remaining_seconds,
                    advisory_title="⚠️ Bottleneck Ahead: Reroute Advised",
                    advisory_message=f"{corridor_sum.vehicle_count} commuters queued. Shortest jam-solving bypass available.",
                    advisory_severity="alert",
                    action="REROUTE",
                    detour_benefit="Save 6–9 minutes via parallel bypass",
                )
            else:
                return UserSignalAdvisory(
                    junction_id=self.junction_id,
                    corridor=corridor,
                    distance_meters=distance_meters,
                    user_signal_lamp=user_lamp,
                    phase_remaining_seconds=self.remaining_seconds,
                    advisory_title="Red Signal - Queuing",
                    advisory_message=f"Hold position. Expected green cycle in ~{self.remaining_seconds + settings.ALL_RED_DURATION}s.",
                    advisory_severity="info",
                    action="HOLD",
                )


class SignalManager:
    def __init__(self):
        self._controllers: Dict[str, JunctionSignalStateMachine] = {}

    def get_or_create(self, junction_id: str, junction_code: str) -> JunctionSignalStateMachine:
        if junction_id not in self._controllers:
            self._controllers[junction_id] = JunctionSignalStateMachine(
                junction_id=junction_id, junction_code=junction_code
            )
        return self._controllers[junction_id]

    def update_all(self):
        for controller in self._controllers.values():
            controller.update_tick()


signal_manager = SignalManager()

