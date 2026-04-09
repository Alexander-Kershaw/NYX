from random import choice

from simulator.assets import GROUND_STATIONS, SOURCE_IPS
from simulator.contracts import AuthStatus, EventType, PayloadStatus, TelemetryEvent
from simulator.event_factory import generate_event_id, generate_event_timestamp
from simulator.state import SatelliteState
from simulator.anomalies import AnomalyType


def event_metadata(state: SatelliteState, event_type: EventType, anomaly_type: AnomalyType | None = None) -> dict[str, object]:

    return {
        "event_id": generate_event_id(),
        "event_timestamp": generate_event_timestamp(),
        "satellite_id": state.satellite_id,
        "ground_station_id": choice(GROUND_STATIONS),
        "event_type": event_type,
        "schema_version": "1.0",
        "source_ip": "203.0.113.250" if anomaly_type == AnomalyType.SPOOFED_SOURCE else choice(SOURCE_IPS),
        "ingest_source": "simulator",
        "is_anomalous": anomaly_type is not None,
        "anomaly_type": anomaly_type.value if anomaly_type else None
    }


def build_heartbeat_event_from_state(state: SatelliteState, anomaly_type: AnomalyType | None = None) -> TelemetryEvent:
    metadata = event_metadata(state, EventType.HEARTBEAT, anomaly_type)

    return TelemetryEvent(
        **metadata,
        payload_status=PayloadStatus.DEGRADED if anomaly_type else PayloadStatus.NOMINAL,
        status_code="WARN" if anomaly_type else "OK",
    )


def build_navigation_event_from_state(state: SatelliteState, anomaly_type: AnomalyType | None = None) -> TelemetryEvent:
    metadata = event_metadata(state, EventType.NAVIGATION, anomaly_type)

    return TelemetryEvent(
        **metadata,
        latitude=state.latitude,
        longitude=state.longitude,
        altitude_km=state.altitude_km,
        velocity_kms=state.velocity_kms,
        payload_status=PayloadStatus.DEGRADED if anomaly_type else PayloadStatus.NOMINAL,
    )


def build_power_event_from_state(state: SatelliteState, anomaly_type: AnomalyType | None = None) -> TelemetryEvent:
    metadata = event_metadata(state, EventType.POWER, anomaly_type)

    return TelemetryEvent(
        **metadata,
        battery_pct=state.battery_pct,
        payload_status=PayloadStatus.DEGRADED if anomaly_type == AnomalyType.BATTERY_DRAIN_SPIKE else PayloadStatus.NOMINAL,
        status_code="PWR_WARN" if anomaly_type == AnomalyType.BATTERY_DRAIN_SPIKE else "PWR_OK",
    )


def build_thermal_event_from_state(state: SatelliteState, anomaly_type: AnomalyType | None = None) -> TelemetryEvent:
    metadata = event_metadata(state, EventType.THERMAL, anomaly_type)

    return TelemetryEvent(
        **metadata,
        temperature_c=state.temperature_c,
        payload_status=PayloadStatus.DEGRADED if anomaly_type == AnomalyType.THERMAL_RUNAWAY else PayloadStatus.NOMINAL,
        status_code="THERM_WARN" if anomaly_type == AnomalyType.THERMAL_RUNAWAY else "THERM_OK",
    )


def build_comms_event_from_state(state: SatelliteState, anomaly_type: AnomalyType | None = None) -> TelemetryEvent:
    metadata = event_metadata(state, EventType.COMMS, anomaly_type)
    spoofed = anomaly_type == AnomalyType.SPOOFED_SOURCE

    return TelemetryEvent(
        **metadata,
        signal_strength_db=state.signal_strength_db,
        uplink_latency_ms=state.uplink_latency_ms,
        downlink_latency_ms=state.downlink_latency_ms,
        packet_integrity_score=0.45 if spoofed else 0.99,
        auth_status=AuthStatus.FAILED if spoofed else AuthStatus.AUTHENTICATED,
        payload_status=PayloadStatus.DEGRADED if anomaly_type == AnomalyType.SIGNAL_DEGRADATION else PayloadStatus.NOMINAL,
        status_code="COMMS_WARN" if anomaly_type == AnomalyType.SIGNAL_DEGRADATION else "COMMS_OK",
    )


def build_spoofing_event_from_state(state: SatelliteState, anomaly_type: AnomalyType | None = None) -> TelemetryEvent:
    metadata = event_metadata(state, EventType.COMMS, anomaly_type)
    spoofed = anomaly_type == AnomalyType.SPOOFED_SOURCE

    return TelemetryEvent(
        **metadata,
        signal_strength_db=state.signal_strength_db,
        uplink_latency_ms=state.uplink_latency_ms,
        downlink_latency_ms=state.downlink_latency_ms,
        packet_integrity_score=0.45 if spoofed else 0.99,
        auth_status=AuthStatus.FAILED if spoofed else AuthStatus.AUTHENTICATED,
        payload_status=PayloadStatus.DEGRADED if spoofed else PayloadStatus.NOMINAL,
        status_code="COMMS_WARN" if spoofed else "COMMS_OK",
    )

