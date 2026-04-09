from simulator.anomalies import AnomalyType, apply_anomaly_to_state
from simulator.contracts import AuthStatus, PayloadStatus
from simulator.state_manager import initialize_satellite_states
from simulator.stateful_event_factory import (
    build_comms_event_from_state,
    build_spoofing_event_from_state,
    build_power_event_from_state,
    build_thermal_event_from_state,
)


def test_battery_drain_spike_reduces_battery() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]
    original_battery = state.battery_pct

    apply_anomaly_to_state(state, AnomalyType.BATTERY_DRAIN_SPIKE)

    assert state.battery_pct < original_battery


def test_thermal_runaway_increases_temperature() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]
    original_temperature = state.temperature_c

    apply_anomaly_to_state(state, AnomalyType.THERMAL_RUNAWAY)

    assert state.temperature_c > original_temperature


def test_signal_degradation_worsens_comms_metrics() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]
    original_signal = state.signal_strength_db
    original_uplink = state.uplink_latency_ms
    original_downlink = state.downlink_latency_ms

    apply_anomaly_to_state(state, AnomalyType.SIGNAL_DEGRADATION)

    assert state.signal_strength_db < original_signal
    assert state.uplink_latency_ms > original_uplink
    assert state.downlink_latency_ms > original_downlink


def test_power_event_marks_anomaly_metadata() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    apply_anomaly_to_state(state, AnomalyType.BATTERY_DRAIN_SPIKE)
    event = build_power_event_from_state(
        state, anomaly_type=AnomalyType.BATTERY_DRAIN_SPIKE
    )

    assert event.is_anomalous is True
    assert event.anomaly_type == "battery_drain_spike"
    assert event.payload_status == PayloadStatus.DEGRADED


def test_thermal_event_marks_anomaly_metadata() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    apply_anomaly_to_state(state, AnomalyType.THERMAL_RUNAWAY)
    event = build_thermal_event_from_state(
        state, anomaly_type=AnomalyType.THERMAL_RUNAWAY
    )

    assert event.is_anomalous is True
    assert event.anomaly_type == "thermal_runaway"
    assert event.payload_status == PayloadStatus.DEGRADED


def test_signal_degradation_event_marks_anomaly_metadata() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    apply_anomaly_to_state(state, AnomalyType.SIGNAL_DEGRADATION)
    event = build_comms_event_from_state(
        state, anomaly_type=AnomalyType.SIGNAL_DEGRADATION
    )

    assert event.is_anomalous is True
    assert event.anomaly_type == "signal_degradation"
    assert event.payload_status == PayloadStatus.DEGRADED


def test_spoofed_source_comms_event_sets_failed_auth() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    event = build_spoofing_event_from_state(
        state, anomaly_type=AnomalyType.SPOOFED_SOURCE
    )

    assert event.is_anomalous is True
    assert event.anomaly_type == "spoofed_source"
    assert event.auth_status == AuthStatus.FAILED
    assert event.source_ip == "203.0.113.250"