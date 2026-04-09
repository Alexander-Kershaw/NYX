from enum import Enum

from simulator.state import SatelliteState

class AnomalyType(str, Enum):
    BATTERY_DRAIN_SPIKE = "battery_drain_spike"
    THERMAL_RUNAWAY = "thermal_runaway"
    SIGNAL_DEGRADATION = "signal_degradation"
    SPOOFED_SOURCE = "spoofed_source"

def apply_battery_drain_spike(state: SatelliteState) -> None:
    state.battery_pct = max(0.0, state.battery_pct - 25.0)

def apply_thermal_runaway(state: SatelliteState) -> None:
    state.temperature_c = min(120.0, state.temperature_c + 35.0)

def apply_signal_degradation(state: SatelliteState) -> None:
    state.signal_strength_db = max(-120.0, state.signal_strength_db - 25.0)
    state.uplink_latency_ms = min(1000.0, state.uplink_latency_ms + 150.0)
    state.downlink_latency_ms = min(1000.0, state.downlink_latency_ms + 150.0)

def apply_anomaly_to_state(state: SatelliteState, anomaly_type: AnomalyType) -> None:
    if anomaly_type == AnomalyType.BATTERY_DRAIN_SPIKE:
        apply_battery_drain_spike(state)

    elif anomaly_type == AnomalyType.THERMAL_RUNAWAY:
        apply_thermal_runaway(state)

    elif anomaly_type == AnomalyType.SIGNAL_DEGRADATION:
        apply_signal_degradation(state)

    elif anomaly_type == AnomalyType.SPOOFED_SOURCE:
        # Spoofed source does not mutate physical satellite state directly.
        return

    else:
        raise ValueError(f"Unsupported anomaly type: {anomaly_type}")