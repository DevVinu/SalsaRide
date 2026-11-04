import pytest
from app.services.signal_controller import JunctionSignalStateMachine
from app.core.constants import SignalPhase, SignalLamp


def test_signal_controller_lamp_mapping():
    sm = JunctionSignalStateMachine("test_junc_1", "TEST_01")
    sm.current_phase = SignalPhase.NORTH_SOUTH_GREEN
    ns_lamp, ew_lamp = sm.get_lamp_states()
    assert ns_lamp == SignalLamp.GREEN
    assert ew_lamp == SignalLamp.RED

    sm.current_phase = SignalPhase.NORTH_SOUTH_YELLOW
    ns_lamp, ew_lamp = sm.get_lamp_states()
    assert ns_lamp == SignalLamp.YELLOW
    assert ew_lamp == SignalLamp.RED

    sm.current_phase = SignalPhase.ALL_RED_TRANSITION_1
    ns_lamp, ew_lamp = sm.get_lamp_states()
    assert ns_lamp == SignalLamp.RED
    assert ew_lamp == SignalLamp.RED

    sm.current_phase = SignalPhase.EAST_WEST_GREEN
    ns_lamp, ew_lamp = sm.get_lamp_states()
    assert ns_lamp == SignalLamp.RED
    assert ew_lamp == SignalLamp.GREEN

