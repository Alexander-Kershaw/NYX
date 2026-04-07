from simulator.state_manager import (
    evolve_comms,
    evolve_navigation,
    evolve_power,
    evolve_thermal,
    initialize_satellite_states,
)


def test_initialize_satellite_states_creates_one_state_per_satellite() -> None:
    states = initialize_satellite_states()

    assert len(states) == 3
    assert "NYX-SAT-001" in states
    assert "NYX-SAT-002" in states
    assert "NYX-SAT-003" in states


def test_evolve_power_keeps_battery_in_valid_range() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    for _ in range(50):
        evolve_power(state)

    assert 0.0 <= state.battery_pct <= 100.0


def test_evolve_navigation_keeps_coordinates_in_valid_range() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    for _ in range(50):
        evolve_navigation(state)

    assert -90.0 <= state.latitude <= 90.0
    assert -180.0 <= state.longitude <= 180.0


def test_evolve_thermal_keeps_temperature_in_valid_range() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    for _ in range(50):
        evolve_thermal(state)

    assert -40.0 <= state.temperature_c <= 80.0


def test_evolve_comms_keeps_metrics_in_valid_range() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    for _ in range(50):
        evolve_comms(state)

    assert -120.0 <= state.signal_strength_db <= -40.0
    assert 1.0 <= state.uplink_latency_ms <= 1000.0
    assert 1.0 <= state.downlink_latency_ms <= 1000.0