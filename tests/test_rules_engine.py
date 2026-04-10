from simulator.alerts import AlertSeverityLevel, AlertType
from simulator.contracts import AuthStatus, EventType, PayloadStatus, TelemetryEvent
from simulator.alert_rules_engine import alert_from_telemetry_event


def test_low_battery_event_raises_alert() -> None:
    event = TelemetryEvent(
        event_id="evt-000001",
        event_timestamp="2026-04-10T10:00:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.POWER,
        schema_version="1.0",
        source_ip="192.168.1.10",
        ingest_source="simulator",
        battery_pct=20.0,
        payload_status=PayloadStatus.DEGRADED,
        status_code="PWR_WARN",
    )

    alerts = alert_from_telemetry_event(event)

    assert any(alert.alert_type == AlertType.LOW_BATTERY for alert in alerts)


def test_high_temperature_event_raises_alert() -> None:
    event = TelemetryEvent(
        event_id="evt-000002",
        event_timestamp="2026-04-10T10:01:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.THERMAL,
        schema_version="1.0",
        source_ip="192.168.1.10",
        ingest_source="simulator",
        temperature_c=75.0,
        payload_status=PayloadStatus.DEGRADED,
        status_code="THERM_WARN",
    )

    alerts = alert_from_telemetry_event(event)

    assert any(alert.alert_type == AlertType.HIGH_TEMPERATURE for alert in alerts)


def test_low_temperature_event_raises_alert() -> None:
    event = TelemetryEvent(
        event_id="evt-000002",
        event_timestamp="2026-04-10T10:01:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.THERMAL,
        schema_version="1.0",
        source_ip="192.168.1.10",
        ingest_source="simulator",
        temperature_c=-50.0,
        payload_status=PayloadStatus.DEGRADED,
        status_code="THERM_WARN",
    )

    alerts = alert_from_telemetry_event(event)

    assert any(alert.alert_type == AlertType.LOW_TEMPERATURE for alert in alerts)


def test_failed_auth_event_raises_critical_alert() -> None:
    event = TelemetryEvent(
        event_id="evt-000003",
        event_timestamp="2026-04-10T10:02:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip="203.0.113.250",
        ingest_source="simulator",
        signal_strength_db=-100.0,
        uplink_latency_ms=300.0,
        downlink_latency_ms=320.0,
        packet_integrity_score=0.45,
        auth_status=AuthStatus.FAILED,
        payload_status=PayloadStatus.DEGRADED,
        status_code="COMMS_WARN",
        is_anomalous=True,
        anomaly_type="spoofed_source",
    )

    alerts = alert_from_telemetry_event(event)

    assert any(alert.alert_type == AlertType.FAILED_AUTHENTICATION for alert in alerts)
    assert any(alert.severity == AlertSeverityLevel.CRITICAL for alert in alerts)
    assert any(alert.alert_type == AlertType.ANOMALY_FLAGGED for alert in alerts)


def test_poor_singal_event_raises_medium_alert() -> None:
    event = TelemetryEvent(
        event_id="evt-000003",
        event_timestamp="2026-04-10T10:02:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip="203.0.113.250",
        ingest_source="simulator",
        signal_strength_db=-200.0,
        uplink_latency_ms=300.0,
        downlink_latency_ms=320.0,
        packet_integrity_score=0.45,
        auth_status=AuthStatus.AUTHENTICATED,
        payload_status=PayloadStatus.DEGRADED,
        status_code="COMMS_WARN",
        is_anomalous=True,
        anomaly_type=None,
    )

    alerts = alert_from_telemetry_event(event)

    assert any(alert.alert_type == AlertType.WEAK_SIGNAL for alert in alerts)
    assert any(alert.severity == AlertSeverityLevel.MEDIUM for alert in alerts)


def test_critial_security_breach_response() -> None:
    event = TelemetryEvent(
        event_id="evt-000003",
        event_timestamp="2026-04-10T10:02:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip="203.0.113.250",
        ingest_source="simulator",
        signal_strength_db=-100.0,
        uplink_latency_ms=300.0,
        downlink_latency_ms=320.0,
        packet_integrity_score=0.45,
        auth_status=AuthStatus.UNKNOWN,
        payload_status=PayloadStatus.DEGRADED,
        status_code="COMMS_WARN",
        is_anomalous=True,
        anomaly_type="spoofed_source",
    )

    alerts = alert_from_telemetry_event(event)

    assert any(alert.alert_type == AlertType.SECURITY_BREACH for alert in alerts)
    assert any(alert.severity == AlertSeverityLevel.CRITICAL for alert in alerts)
    assert any(alert.alert_type == AlertType.ANOMALY_FLAGGED for alert in alerts)