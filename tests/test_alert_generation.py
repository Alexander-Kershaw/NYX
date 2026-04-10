import json
from pathlib import Path

from simulator.generate_alerts import generate_alerts_from_telemetry_jsonl


def test_generate_alerts_from_jsonl_creates_summary(tmp_path: Path) -> None:
    telemetry_path = tmp_path / "telemetry.jsonl"
    alerts_path = tmp_path / "alerts.jsonl"

    record = {
        "event_id": "evt-000001",
        "event_timestamp": "2026-04-10T10:00:00Z",
        "satellite_id": "NYX-SAT-001",
        "ground_station_id": "GND-UK-001",
        "event_type": "power",
        "schema_version": "1.0",
        "source_ip": "192.168.1.10",
        "ingest_source": "simulator",
        "battery_pct": 20.0,
        "payload_status": "degraded",
        "status_code": "PWR_WARN",
        "is_anomalous": True,
        "anomaly_type": "battery_drain_spike",
    }

    with telemetry_path.open("w", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    summary = generate_alerts_from_telemetry_jsonl(
        telemetry_filepath=telemetry_path,
        alert_summary_output_path=alerts_path,
    )

    assert summary.total_events_processed == 1
    assert summary.total_alerts >= 1
    assert alerts_path.exists()