import pytest
from pydantic import ValidationError

from simulator.contracts import (AuthStatus, EventType, PayloadStatus, TelemetryEvent)

def test_valid_navigation_event_passes() -> None:
    event = TelemetryEvent(
        event_id="evt-100001",
        event_timestamp="2026-04-06T12:00:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.NAVIGATION,
        schema_version="1.0",
        source_ip="192.168.1.10",
        ingest_source="simulator",
        latitude=52.0,
        longitude=-1.2,
        altitude_km=540.5,
        velocity_kms=7.67,
        payload_status=PayloadStatus.NOMINAL,
    )

    assert event.event_type == EventType.NAVIGATION
    assert event.latitude == 52.0
    assert event.velocity_kms == 7.67


def test_navigation_event_missing_latitude_fails() -> None:
    with pytest.raises(ValidationError, match="latitude"):
        TelemetryEvent(
            event_id="evt-100002",
            event_timestamp="2026-04-06T12:01:00Z",
            satellite_id="NYX-SAT-002",
            ground_station_id="GND-UK-001",
            event_type=EventType.NAVIGATION,
            schema_version="1.0",
            source_ip="192.168.1.11",
            ingest_source="simulator",
            longitude=-1.0,
            altitude_km=541.0,
            velocity_kms=7.70,
        )


def test_battery_percentage_out_of_range_fails() -> None:
    with pytest.raises(ValidationError, match="battery_pct must be between 0 and 100"):
        TelemetryEvent(
            event_id="evt-100003",
            event_timestamp="2026-04-06T12:02:00Z",
            satellite_id="NYX-SAT-001",
            ground_station_id="GND-UK-001",
            event_type=EventType.POWER,
            schema_version="1.0",
            source_ip="192.168.1.12",
            ingest_source="simulator",
            battery_pct=150.0,
        )


def test_packet_integrity_score_out_of_range_fails() -> None:
    with pytest.raises(
        ValidationError, match="packet_integrity_score must be between 0 and 1"
    ):
        TelemetryEvent(
            event_id="evt-100004",
            event_timestamp="2026-04-06T12:03:00Z",
            satellite_id="NYX-SAT-003",
            ground_station_id="GND-NO-001",
            event_type=EventType.COMMS,
            schema_version="1.0",
            source_ip="192.168.1.13",
            ingest_source="simulator",
            signal_strength_db=-82.0,
            uplink_latency_ms=120.0,
            downlink_latency_ms=140.0,
            packet_integrity_score=1.5,
            auth_status=AuthStatus.AUTHENTICATED,
        )


def test_valid_comms_event_passes() -> None:
    event = TelemetryEvent(
        event_id="evt-100005",
        event_timestamp="2026-04-06T12:04:00Z",
        satellite_id="NYX-SAT-003",
        ground_station_id="GND-NO-001",
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip="192.168.1.14",
        ingest_source="simulator",
        signal_strength_db=-78.5,
        uplink_latency_ms=95.0,
        downlink_latency_ms=101.0,
        packet_integrity_score=0.98,
        auth_status=AuthStatus.AUTHENTICATED,
        payload_status=PayloadStatus.NOMINAL,
    )

    assert event.event_type == EventType.COMMS
    assert event.packet_integrity_score == 0.98
    assert event.auth_status == AuthStatus.AUTHENTICATED