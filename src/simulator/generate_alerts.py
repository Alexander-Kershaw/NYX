import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from simulator.alert_summary import AlertRunSummary
from simulator.contracts import TelemetryEvent
from simulator.alert_rules_engine import alert_from_telemetry_event


def generate_alerts_from_telemetry_jsonl(
        telemetry_filepath: str | Path,
        alert_summary_output_path: str | Path | None = None
) -> AlertRunSummary:
    
    telemetry_filepath = Path(telemetry_filepath)
    alert_summary_output_path = Path(alert_summary_output_path) if alert_summary_output_path else None

    total_events_processed = 0
    total_alerts_generated = 0
    alerts_by_EventType: Counter[str] = Counter()
    alerts_by_AlertSeverity: Counter[str] = Counter()

    output_file = None
    if alert_summary_output_path is not None:
        output_file = alert_summary_output_path.open("w", encoding="utf-8")

    
    try:
        with telemetry_filepath.open("r", encoding="utf-8") as telemetry_file:
            for line in telemetry_file:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
            
                try:
                    raw_telemetry_record = json.loads(stripped_line)
                    event = TelemetryEvent(**raw_telemetry_record)
                except (json.JSONDecodeError, ValidationError):
                    continue

                total_events_processed += 1
                alerts = alert_from_telemetry_event(event)

                for alert in alerts:
                    total_alerts_generated += 1
                    alerts_by_EventType[alert.event_type] += 1
                    alerts_by_AlertSeverity[alert.severity] += 1

                    if output_file is not None:
                        output_file.write(
                            json.dumps(alert.model_dump(mode="json")) + "\n"
                        )

    finally:
        if output_file is not None:
            output_file.close()

    
    return AlertRunSummary(
        telemetry_filepath=str(telemetry_filepath),
        alert_output_filepath=str(alert_summary_output_path) if alert_summary_output_path else None,
        total_events_processed=total_events_processed,
        total_alerts=total_alerts_generated,
        alerts_by_type=dict(alerts_by_EventType),
        alerts_by_severity=dict(alerts_by_AlertSeverity)
    )

