import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from simulator.analysis_summary import NumericMetricSummary, TelemetryAnalysisSummary
from simulator.contracts import TelemetryEvent


def summarize_numeric_values(values: list[float]) -> NumericMetricSummary:
    if not values:
        return NumericMetricSummary()

    return NumericMetricSummary(
        minimum=min(values),
        maximum=max(values),
        average=sum(values) / len(values),
    )


def analyze_jsonl_file(filepath: str | Path) -> TelemetryAnalysisSummary:

    path = Path(filepath)

    valid_events: list[TelemetryEvent] = []
    events_by_type: Counter[str] = Counter()
    anomalies_by_type: Counter[str] = Counter()
    anomaly_events = 0

    battery_values: list[float] = []
    temperature_values: list[float] = []
    uplink_latency_values: list[float] = []
    downlink_latency_values: list[float] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()

            if not stripped:
                continue

            try:
                raw_record = json.loads(stripped)
                event = TelemetryEvent(**raw_record)
                valid_events.append(event)

                events_by_type[event.event_type.value] += 1

                if event.is_anomalous:
                    anomaly_events += 1
                    if event.anomaly_type is not None:
                        anomalies_by_type[event.anomaly_type] += 1

                if event.battery_pct is not None:
                    battery_values.append(event.battery_pct)

                if event.temperature_c is not None:
                    temperature_values.append(event.temperature_c)

                if event.uplink_latency_ms is not None:
                    uplink_latency_values.append(event.uplink_latency_ms)

                if event.downlink_latency_ms is not None:
                    downlink_latency_values.append(event.downlink_latency_ms)

            except (json.JSONDecodeError, ValidationError):

                continue

    total_valid_events = len(valid_events)
    anomaly_rate = (anomaly_events / total_valid_events if total_valid_events > 0 else 0.0)

    return TelemetryAnalysisSummary(
        filepath=str(path),
        total_valid_events=total_valid_events,
        anomaly_events=anomaly_events,
        anomaly_rate=anomaly_rate,
        events_by_type=dict(events_by_type),
        anomalies_by_type=dict(anomalies_by_type),
        battery_pct=summarize_numeric_values(battery_values),
        temperature_c=summarize_numeric_values(temperature_values),
        uplink_latency_ms=summarize_numeric_values(uplink_latency_values),
        downlink_latency_ms=summarize_numeric_values(downlink_latency_values),
    )