import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from simulator.contracts import TelemetryEvent
from simulator.validation_summary import TelemetryValidationSummary

def validate_telemetry_jsonl(file_path: str | Path) -> TelemetryValidationSummary:

    jsonl_path = Path(file_path)

    total_records = 0 
    valid_records = 0
    invalid_records = 0

    count_event_types: Counter[str] = Counter()
    anomalies_by_event_type: Counter[str] = Counter()
    invalid_sample: list[str] = []

    with jsonl_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped_line = line.strip()

            if not stripped_line:
                continue
        
            total_records += 1

            try:
                raw_telemetry = json.loads(stripped_line)
                event = TelemetryEvent(**raw_telemetry)
                valid_records += 1
                count_event_types[event.event_type.value] += 1

                if event.is_anomalous and event.anomaly_type is not None:
                    anomalies_by_event_type[event.anomaly_type] += 1
        
            except (json.JSONDecodeError, ValidationError) as exc:
                invalid_records += 1
                
                if len(invalid_sample) < 5:
                    invalid_sample.append(f"Line {line_number}: {exc}")

    return TelemetryValidationSummary(
        filepath=str(jsonl_path),
        total_records=total_records,
        valid_records=valid_records,
        invalid_records=invalid_records,
        events_by_type=dict(count_event_types),
        anomalies_by_type=dict(anomalies_by_event_type),
        invalid_sample=invalid_sample,
    )

