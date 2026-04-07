from random import choice

from simulator.assets import GROUND_STATIONS, SOURCE_IPS
from simulator.contracts import AuthStatus, EventType, PayloadStatus, TelemetryEvent
from simulator.event_factory import generate_event_id, generate_event_timestamp
from simulator.state import SatelliteState


def build_heartbeat_event_from_state(state: SatelliteState) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=state.satellite_id,
        ground_station_id=choice(GROUND_STATIONS),
        event_type=EventType.HEARTBEAT,
        schema_version="1.0",
        source_ip=choice(SOURCE_IPS),
        ingest_source="simulator",
        payload_status=PayloadStatus.NOMINAL,
        status_code="OK",
    )


def build_navigation_event_from_state(state: SatelliteState) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=state.satellite_id,
        ground_station_id=choice(GROUND_STATIONS),
        event_type=EventType.NAVIGATION,
        schema_version="1.0",
        source_ip=choice(SOURCE_IPS),
        ingest_source="simulator",
        latitude=state.latitude,
        longitude=state.longitude,
        altitude_km=state.altitude_km,
        velocity_kms=state.velocity_kms,
        payload_status=PayloadStatus.NOMINAL,
    )


def build_power_event_from_state(state: SatelliteState) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=state.satellite_id,
        ground_station_id=choice(GROUND_STATIONS),
        event_type=EventType.POWER,
        schema_version="1.0",
        source_ip=choice(SOURCE_IPS),
        ingest_source="simulator",
        battery_pct=state.battery_pct,
        payload_status=PayloadStatus.NOMINAL,
        status_code="PWR_OK",
    )


def build_thermal_event_from_state(state: SatelliteState) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=state.satellite_id,
        ground_station_id=choice(GROUND_STATIONS),
        event_type=EventType.THERMAL,
        schema_version="1.0",
        source_ip=choice(SOURCE_IPS),
        ingest_source="simulator",
        temperature_c=state.temperature_c,
        payload_status=PayloadStatus.NOMINAL,
        status_code="THERM_OK",
    )


def build_comms_event_from_state(state: SatelliteState) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=state.satellite_id,
        ground_station_id=choice(GROUND_STATIONS),
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip=choice(SOURCE_IPS),
        ingest_source="simulator",
        signal_strength_db=state.signal_strength_db,
        uplink_latency_ms=state.uplink_latency_ms,
        downlink_latency_ms=state.downlink_latency_ms,
        packet_integrity_score=0.99,
        auth_status=AuthStatus.AUTHENTICATED,
        payload_status=PayloadStatus.NOMINAL,
        status_code="COMMS_OK",
    )