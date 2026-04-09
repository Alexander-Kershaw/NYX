import json
from pathlib import Path

from simulator.reader import validate_telemetry_jsonl


def test_validate_jsonl_file_counts_valid_records(tmp_path: Path) -> None:
    filepath = tmp_path / "valid_events.jsonl"

    records = [
        {
            "event_id": "evt-000001",
            "event_timestamp": "2026-04-09T06:00:00Z",
            "satellite_id": "NYX-SAT-001",
            "ground_station_id": "GND-UK-001",
            "event_type": "power",
            "schema_version": "1.0",
            "source_ip": "192.168.1.10",
            "ingest_source": "simulator",
            "battery_pct": 88.0,
            "payload_status": "nominal",
            "status_code": "PWR_OK",
            "is_anomalous": False,
            "anomaly_type": None,
        },
        {
            "event_id": "evt-000002",
            "event_timestamp": "2026-04-09T06:00:01Z",
            "satellite_id": "NYX-SAT-001",
            "ground_station_id": "GND-UK-001",
            "event_type": "thermal",
            "schema_version": "1.0",
            "source_ip": "192.168.1.10",
            "ingest_source": "simulator",
            "temperature_c": 24.0,
            "payload_status": "nominal",
            "status_code": "THERM_OK",
            "is_anomalous": False,
            "anomaly_type": None,
        },
    ]

    with filepath.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    summary = validate_telemetry_jsonl(filepath)

    assert summary.total_records == 2
    assert summary.valid_records == 2
    assert summary.invalid_records == 0
    assert summary.events_by_type == {"power": 1, "thermal": 1}
    assert summary.anomalies_by_type == {}


def test_validate_jsonl_file_counts_invalid_records(tmp_path: Path) -> None:
    filepath = tmp_path / "mixed_events.jsonl"

    valid_record = {
        "event_id": "evt-000003",
        "event_timestamp": "2026-04-09T06:00:02Z",
        "satellite_id": "NYX-SAT-002",
        "ground_station_id": "GND-NO-001",
        "event_type": "comms",
        "schema_version": "1.0",
        "source_ip": "192.168.1.11",
        "ingest_source": "simulator",
        "signal_strength_db": -72.0,
        "uplink_latency_ms": 80.0,
        "downlink_latency_ms": 90.0,
        "packet_integrity_score": 0.99,
        "auth_status": "authenticated",
        "payload_status": "nominal",
        "status_code": "COMMS_OK",
        "is_anomalous": False,
        "anomaly_type": None,
    }

    invalid_record = {
        "event_id": "evt-000004",
        "event_timestamp": "2026-04-09T06:00:03Z",
        "satellite_id": "NYX-SAT-002",
        "ground_station_id": "GND-NO-001",
        "event_type": "power",
        "schema_version": "1.0",
        "source_ip": "192.168.1.11",
        "ingest_source": "simulator",
        "battery_pct": 150.0,
        "payload_status": "nominal",
        "status_code": "PWR_OK",
        "is_anomalous": False,
        "anomaly_type": None,
    }

    with filepath.open("w", encoding="utf-8") as file:
        file.write(json.dumps(valid_record) + "\n")
        file.write(json.dumps(invalid_record) + "\n")

    summary = validate_telemetry_jsonl(filepath)

    assert summary.total_records == 2
    assert summary.valid_records == 1
    assert summary.invalid_records == 1
    assert summary.events_by_type == {"comms": 1}
    assert len(summary.invalid_sample) == 1


def test_validate_jsonl_file_counts_anomalies(tmp_path: Path) -> None:
    filepath = tmp_path / "anomalous_events.jsonl"

    anomalous_record = {
        "event_id": "evt-000005",
        "event_timestamp": "2026-04-09T06:00:04Z",
        "satellite_id": "NYX-SAT-003",
        "ground_station_id": "GND-UK-001",
        "event_type": "thermal",
        "schema_version": "1.0",
        "source_ip": "192.168.1.12",
        "ingest_source": "simulator",
        "temperature_c": 70.0,
        "payload_status": "degraded",
        "status_code": "THERM_WARN",
        "is_anomalous": True,
        "anomaly_type": "thermal_runaway",
    }

    with filepath.open("w", encoding="utf-8") as file:
        file.write(json.dumps(anomalous_record) + "\n")

    summary = validate_telemetry_jsonl(filepath)

    assert summary.total_records == 1
    assert summary.valid_records == 1
    assert summary.invalid_records == 0
    assert summary.events_by_type == {"thermal": 1}
    assert summary.anomalies_by_type == {"thermal_runaway": 1}
