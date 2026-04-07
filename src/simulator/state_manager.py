from random import uniform

from simulator.assets import SATELLITES
from simulator.state import SatelliteState

# Initial satellite states for each satellite in the constellation, with random values within realistic ranges.
def initialize_satellite_states() -> dict[str, SatelliteState]:
    states: dict[str, SatelliteState] = {}

    for satellite_id in SATELLITES:
        states[satellite_id] = SatelliteState(
            satellite_id=satellite_id,
            latitude=uniform(-60.0, 60.0),
            longitude=uniform(-180.0, 180.0),
            altitude_km=uniform(500.0, 550.0),
            velocity_kms=uniform(7.5, 8.0),
            battery_pct=uniform(70.0, 100.0),
            temperature_c=uniform(-10.0, 35.0),
            signal_strength_db=uniform(-80.0, -60.0),
            uplink_latency_ms=uniform(50.0, 100.0),
            downlink_latency_ms=uniform(50.0, 100.0),
        )

    return states

# Evolve the position and velocity slightly 
def evolve_navigation(state: SatelliteState) -> None:
    state.latitude = max(-90.0, min(90.0, state.latitude + uniform(-0.5, 0.5)))
    state.longitude = max(-180.0, min(180.0, state.longitude + uniform(-1.0, 1.0)))
    state.altitude_km = max(450.0, min(600.0, state.altitude_km + uniform(-0.5, 0.5)))
    state.velocity_kms = max(7.0, min(8.5, state.velocity_kms + uniform(-0.02, 0.02)))

# Slight downwards drift tendency for battery percentage, with occasional small recharges (e.g. from solar panels).
def evolve_power(state: SatelliteState) -> None:
    state.battery_pct = max(0.0, min(100.0, state.battery_pct + uniform(-0.4, 0.1)))

# Temperature can fluctuate within a safe range
def evolve_thermal(state: SatelliteState) -> None:
    state.temperature_c = max(-40.0, min(80.0, state.temperature_c + uniform(-1.0, 1.0)))

# Signal strength and latency can fluctuate
def evolve_comms(state: SatelliteState) -> None:
    state.signal_strength_db = max(-120.0, min(-40.0, state.signal_strength_db + uniform(-1.5, 1.5)))
    state.uplink_latency_ms = max(1.0, min(1000.0, state.uplink_latency_ms + uniform(-5.0, 5.0)))
    state.downlink_latency_ms = max(1.0, min(1000.0, state.downlink_latency_ms + uniform(-5.0, 5.0)))