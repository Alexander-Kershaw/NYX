from pathlib import Path

from simulator.analysis_summary import TelemetryAnalysisSummary
from simulator.analysis_output import analyze_jsonl_file
from simulator.comparison_summary import MetricDeltaSummary, TelemetryComparisonSummary


def build_metric_delta(baseline: float | None, candidate: float | None) -> MetricDeltaSummary:
    if baseline is None or candidate is None:
        return MetricDeltaSummary(
            baseline=baseline,
            candidate=candidate,
            delta=None,
        )

    return MetricDeltaSummary(
        baseline=baseline,
        candidate=candidate,
        delta=candidate - baseline,
    )


def compare_analysis_summaries(baseline: TelemetryAnalysisSummary, candidate: TelemetryAnalysisSummary
                               ) -> TelemetryComparisonSummary:
    return TelemetryComparisonSummary(
        baseline_filepath=baseline.filepath,
        candidate_filepath=candidate.filepath,
        baseline_total_valid_events=baseline.total_valid_events,
        candidate_total_valid_events=candidate.total_valid_events,
        baseline_anomaly_events=baseline.anomaly_events,
        candidate_anomaly_events=candidate.anomaly_events,
        baseline_anomaly_rate=baseline.anomaly_rate,
        candidate_anomaly_rate=candidate.anomaly_rate,
        anomaly_rate_delta=candidate.anomaly_rate - baseline.anomaly_rate,
        baseline_events_by_type=baseline.events_by_type,
        candidate_events_by_type=candidate.events_by_type,
        baseline_anomalies_by_type=baseline.anomalies_by_type,
        candidate_anomalies_by_type=candidate.anomalies_by_type,
        battery_pct_average=build_metric_delta(baseline.battery_pct.average, candidate.battery_pct.average),
        temperature_c_average=build_metric_delta(baseline.temperature_c.average, candidate.temperature_c.average),
        uplink_latency_ms_average=build_metric_delta(baseline.uplink_latency_ms.average, candidate.uplink_latency_ms.average),
        downlink_latency_ms_average=build_metric_delta(baseline.downlink_latency_ms.average, candidate.downlink_latency_ms.average)
    )


def compare_jsonl_files(baseline_filepath: str | Path, candidate_filepath: str | Path
                        ) -> TelemetryComparisonSummary:
    baseline_summary = analyze_jsonl_file(baseline_filepath)
    candidate_summary = analyze_jsonl_file(candidate_filepath)

    return compare_analysis_summaries(baseline_summary, candidate_summary)