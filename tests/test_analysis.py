import json
from pathlib import Path

from simulator.analysis_output import analyze_jsonl_file, summarize_numeric_values


def test_summarize_numeric_values_returns_empty_summary_for_empty_list() -> None:
    summary = summarize_numeric_values([])

    assert summary.minimum is None
    assert summary.maximum is None
    assert summary.average is None


def test_summarize_numeric_values_returns_expected_stats() -> None:
    summary = summarize_numeric_values([10.0, 20.0, 30.0])

    assert summary.minimum == 10.0
    assert summary.maximum == 30.0
    assert summary.average == 20.0


def test_analyze_jsonl_file_computes_metrics_from_valid_records(tmp_path: Path) -> None:
    filepath = tmp_path / "analysis_events.jsonl"

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
            "battery_pct": 80.0,
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
            "temperature_c": 25.0,
            "payload_status": "degraded",
            "status_code": "THERM_WARN",
            "is_anomalous": True,
            "anomaly_type": "thermal_runaway",
        },
        {
            "event_id": "evt-000003",
            "event_timestamp": "2026-04-09T06:00:02Z",
            "satellite_id": "NYX-SAT-001",
            "ground_station_id": "GND-UK-001",
            "event_type": "comms",
            "schema_version": "1.0",
            "source_ip": "192.168.1.10",
            "ingest_source": "simulator",
            "signal_strength_db": -70.0,
            "uplink_latency_ms": 100.0,
            "downlink_latency_ms": 120.0,
            "packet_integrity_score": 0.98,
            "auth_status": "authenticated",
            "payload_status": "nominal",
            "status_code": "COMMS_OK",
            "is_anomalous": False,
            "anomaly_type": None,
        },
    ]

    with filepath.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    summary = analyze_jsonl_file(filepath)

    assert summary.total_valid_events == 3
    assert summary.anomaly_events == 1
    assert summary.anomaly_rate == 1 / 3
    assert summary.events_by_type == {
        "power": 1,
        "thermal": 1,
        "comms": 1,
    }
    assert summary.anomalies_by_type == {"thermal_runaway": 1}
    assert summary.battery_pct.minimum == 80.0
    assert summary.battery_pct.maximum == 80.0
    assert summary.battery_pct.average == 80.0
    assert summary.temperature_c.minimum == 25.0
    assert summary.temperature_c.maximum == 25.0
    assert summary.uplink_latency_ms.average == 100.0
    assert summary.downlink_latency_ms.average == 120.0


def test_analyze_jsonl_file_ignores_invalid_records(tmp_path: Path) -> None:
    filepath = tmp_path / "mixed_analysis_events.jsonl"

    valid_record = {
        "event_id": "evt-000010",
        "event_timestamp": "2026-04-09T06:00:10Z",
        "satellite_id": "NYX-SAT-002",
        "ground_station_id": "GND-NO-001",
        "event_type": "power",
        "schema_version": "1.0",
        "source_ip": "192.168.1.11",
        "ingest_source": "simulator",
        "battery_pct": 75.0,
        "payload_status": "nominal",
        "status_code": "PWR_OK",
        "is_anomalous": False,
        "anomaly_type": None,
    }

    invalid_record = {
        "event_id": "evt-000011",
        "event_timestamp": "2026-04-09T06:00:11Z",
        "satellite_id": "NYX-SAT-002",
        "ground_station_id": "GND-NO-001",
        "event_type": "power",
        "schema_version": "1.0",
        "source_ip": "192.168.1.11",
        "ingest_source": "simulator",
        "battery_pct": 200.0,
        "payload_status": "nominal",
        "status_code": "PWR_OK",
        "is_anomalous": False,
        "anomaly_type": None,
    }

    with filepath.open("w", encoding="utf-8") as file:
        file.write(json.dumps(valid_record) + "\n")
        file.write(json.dumps(invalid_record) + "\n")

    summary = analyze_jsonl_file(filepath)

    assert summary.total_valid_events == 1
    assert summary.anomaly_events == 0
    assert summary.events_by_type == {"power": 1}
    assert summary.battery_pct.average == 75.0