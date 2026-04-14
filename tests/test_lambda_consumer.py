import base64
import json
from datetime import UTC, datetime

from cloud.lambda_consumer import build_s3_object_key, decode_kinesis_record, build_quarantine_record


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