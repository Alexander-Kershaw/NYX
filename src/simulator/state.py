from pydantic import BaseModel

# This is the memory of the satellite's current state, which can be updated by telemetry events
class SatelliteState(BaseModel):
    satellite_id: str
    latitude: float
    longitude: float
    altitude_km: float
    velocity_kms: float
    battery_pct: float
    temperature_c: float
    signal_strength_db: float
    uplink_latency_ms: float
    downlink_latency_ms: float

