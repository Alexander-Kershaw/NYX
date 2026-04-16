import base64
import json
from datetime import UTC, datetime

from cloud.lambda_consumer import (
    build_s3_object_key,
    decode_kinesis_record,
    build_quarantine_record,
    evaluate_sns_alert,
    build_alert_message,
    publish_cloudwatch_metrics
)

from simulator.contracts import (
    AuthStatus,
    EventType,
    PayloadStatus,
    TelemetryEvent
)

from unittest.mock import patch


def test_build_s3_object_key_returns_expected_prefix_structure() -> None:
    timestamp = datetime(2026, 4, 11, 10, 0, 0, tzinfo=UTC)

    key = build_s3_object_key(
        prefix="bronze/telemetry",
        timestamp=timestamp,
        batch_id="test-batch-123",
    )

    assert key == (
        "bronze/telemetry/"
        "ingestion_date=2026-04-11/"
        "batch_test-batch-123.jsonl"
    )


def test_decode_kinesis_record_decodes_valid_json_payload() -> None:
    payload = {
        "event_id": "evt-000001",
        "satellite_id": "NYX-SAT-001",
        "event_type": "navigation",
    }
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    record = {
        "kinesis": {
            "data": encoded,
        }
    }

    decoded = decode_kinesis_record(record)

    assert decoded == payload


def test_decode_kinesis_record_returns_none_for_invalid_payload() -> None:
    record = {
        "kinesis": {
            "data": "not-valid-base64!!!",
        }
    }

    decoded = decode_kinesis_record(record)

    assert decoded is None


def test_build_quarantine_record_wraps_error_metadata() -> None:
    raw_record = {"event_id": "evt-999999", "battery_pct": 150.0}

    quarantine_record = build_quarantine_record(
        raw_record=raw_record,
        error_message="battery_pct must be between 0 and 100",
        ingestion_timestamp="2026-04-11T10:00:00Z",
    )

    assert quarantine_record["ingestion_timestamp"] == "2026-04-11T10:00:00Z"
    assert quarantine_record["error_type"] == "validation_error"
    assert "battery_pct must be between 0 and 100" in quarantine_record["error_message"]
    assert quarantine_record["raw_record"] == raw_record


def test_should_publish_alert_for_anomalous_event() -> None:
    event = TelemetryEvent(
        event_id="evt-100001",
        event_timestamp="2026-04-11T12:00:00Z",
        satellite_id="NYX-SAT-001",
        ground_station_id="GND-UK-001",
        event_type=EventType.POWER,
        schema_version="1.0",
        source_ip="192.168.1.10",
        ingest_source="simulator",
        battery_pct=22.0,
        payload_status=PayloadStatus.DEGRADED,
        status_code="PWR_WARN",
        is_anomalous=True,
        anomaly_type="battery_drain_spike",
    )

    should_alert, reasons = evaluate_sns_alert(event)

    assert should_alert is True
    assert any("anomalous" in reason.lower() for reason in reasons)


def test_should_publish_alert_for_failed_auth() -> None:
    event = TelemetryEvent(
        event_id="evt-100002",
        event_timestamp="2026-04-11T12:00:01Z",
        satellite_id="NYX-SAT-002",
        ground_station_id="GND-UK-001",
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip="203.0.113.250",
        ingest_source="simulator",
        signal_strength_db=-100.0,
        uplink_latency_ms=250.0,
        downlink_latency_ms=260.0,
        packet_integrity_score=0.45,
        auth_status=AuthStatus.FAILED,
        payload_status=PayloadStatus.DEGRADED,
        status_code="COMMS_WARN",
        is_anomalous=True,
        anomaly_type="spoofed_source",
    )

    should_alert, reasons = evaluate_sns_alert(event)

    assert should_alert is True
    assert any("authentication" in reason.lower() for reason in reasons)


def test_build_alert_message_contains_key_fields() -> None:
    event = TelemetryEvent(
        event_id="evt-100003",
        event_timestamp="2026-04-11T12:00:02Z",
        satellite_id="NYX-SAT-003",
        ground_station_id="GND-UK-001",
        event_type=EventType.THERMAL,
        schema_version="1.0",
        source_ip="192.168.1.10",
        ingest_source="simulator",
        temperature_c=72.0,
        payload_status=PayloadStatus.DEGRADED,
        status_code="THERM_WARN",
        is_anomalous=True,
        anomaly_type="thermal_runaway",
    )

    subject, message = build_alert_message(event, ["Temperature exceeded threshold"])

    assert "NYX Alert" in subject
    assert event.satellite_id in subject
    assert event.event_id in message
    assert "Temperature exceeded threshold" in message


@patch("cloud.lambda_consumer.cloudwatch_client")
def test_publish_cloudwatch_metrics_sends_expected_metric_count(mock_cloudwatch_client) -> None:
    publish_cloudwatch_metrics(
        namespace="NYX/Ingestion",
        received_records=10,
        decoded_records=10,
        silver_records=9,
        quarantine_records=1,
        alerts_published=2,
    )

    mock_cloudwatch_client.put_metric_data.assert_called_once()
    kwargs = mock_cloudwatch_client.put_metric_data.call_args.kwargs

    assert kwargs["Namespace"] == "NYX/Ingestion"
    assert len(kwargs["MetricData"]) == 5