from simulator.contracts import AuthStatus, EventType
from simulator.event_factory import (
    build_comms_event,
    build_heartbeat_event,
    build_navigation_event,
    build_power_event,
    build_thermal_event,
)


def test_build_navigation_event_returns_navigation_event() -> None:
    event = build_navigation_event()

    assert event.event_type == EventType.NAVIGATION
    assert event.latitude is not None
    assert event.longitude is not None
    assert event.altitude_km is not None
    assert event.velocity_kms is not None
    assert event.schema_version == "1.0"
    assert event.ingest_source == "simulator"


def test_build_navigation_event_respects_explicit_identifiers() -> None:
    event = build_navigation_event(
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        source_ip="192.168.1.99",
    )

    assert event.satellite_id == "NYX-SAT-001"
    assert event.ground_station_id == "GND-UK-001"
    assert event.source_ip == "192.168.1.99"


def test_build_heartbeat_event_returns_heartbeat_event() -> None:
    event = build_heartbeat_event()

    assert event.event_type == EventType.HEARTBEAT
    assert event.payload_status is not None
    assert event.status_code == "OK"


def test_build_power_event_returns_power_event() -> None:
    event = build_power_event()

    assert event.event_type == EventType.POWER
    assert event.battery_pct is not None
    assert 0 <= event.battery_pct <= 100


def test_build_thermal_event_returns_thermal_event() -> None:
    event = build_thermal_event()

    assert event.event_type == EventType.THERMAL
    assert event.temperature_c is not None


def test_build_comms_event_returns_comms_event() -> None:
    event = build_comms_event()

    assert event.event_type == EventType.COMMS
    assert event.signal_strength_db is not None
    assert event.uplink_latency_ms is not None
    assert event.downlink_latency_ms is not None
    assert event.packet_integrity_score is not None
    assert event.auth_status == AuthStatus.AUTHENTICATED