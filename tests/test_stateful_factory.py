from simulator.contracts import EventType
from simulator.state_manager import initialize_satellite_states
from simulator.stateful_event_factory import (
    build_comms_event_from_state,
    build_navigation_event_from_state,
    build_power_event_from_state,
    build_thermal_event_from_state,
)


def test_build_navigation_event_from_state_uses_state_values() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    event = build_navigation_event_from_state(state)

    assert event.event_type == EventType.NAVIGATION
    assert event.satellite_id == state.satellite_id
    assert event.latitude == state.latitude
    assert event.longitude == state.longitude


def test_build_power_event_from_state_uses_state_values() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    event = build_power_event_from_state(state)

    assert event.event_type == EventType.POWER
    assert event.battery_pct == state.battery_pct


def test_build_thermal_event_from_state_uses_state_values() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    event = build_thermal_event_from_state(state)

    assert event.event_type == EventType.THERMAL
    assert event.temperature_c == state.temperature_c


def test_build_comms_event_from_state_uses_state_values() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    event = build_comms_event_from_state(state)

    assert event.event_type == EventType.COMMS
    assert event.signal_strength_db == state.signal_strength_db
    assert event.uplink_latency_ms == state.uplink_latency_ms
    assert event.downlink_latency_ms == state.downlink_latency_ms