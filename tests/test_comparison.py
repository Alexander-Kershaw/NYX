from simulator.analysis_summary import NumericMetricSummary, TelemetryAnalysisSummary
from simulator.compare_runs import build_metric_delta, compare_analysis_summaries


def test_build_metric_delta_handles_missing_values() -> None:
    result = build_metric_delta(None, 10.0)

    assert result.baseline is None
    assert result.candidate == 10.0
    assert result.delta is None


def test_build_metric_delta_computes_difference() -> None:
    result = build_metric_delta(10.0, 15.5)

    assert result.baseline == 10.0
    assert result.candidate == 15.5
    assert result.delta == 5.5


def test_compare_analysis_summaries_returns_expected_deltas() -> None:
    baseline = TelemetryAnalysisSummary(
        filepath="baseline.jsonl",
        total_valid_events=10,
        anomaly_events=2,
        anomaly_rate=0.2,
        events_by_type={"power": 2, "thermal": 2},
        anomalies_by_type={"thermal_runaway": 2},
        battery_pct=NumericMetricSummary(minimum=70.0, maximum=90.0, average=80.0),
        temperature_c=NumericMetricSummary(minimum=20.0, maximum=40.0, average=30.0),
        uplink_latency_ms=NumericMetricSummary(minimum=50.0, maximum=90.0, average=70.0),
        downlink_latency_ms=NumericMetricSummary(minimum=55.0, maximum=95.0, average=75.0),
    )

    candidate = TelemetryAnalysisSummary(
        filepath="candidate.jsonl",
        total_valid_events=10,
        anomaly_events=5,
        anomaly_rate=0.5,
        events_by_type={"power": 2, "thermal": 2},
        anomalies_by_type={"thermal_runaway": 3, "spoofed_source": 2},
        battery_pct=NumericMetricSummary(minimum=50.0, maximum=85.0, average=65.0),
        temperature_c=NumericMetricSummary(minimum=25.0, maximum=75.0, average=45.0),
        uplink_latency_ms=NumericMetricSummary(minimum=60.0, maximum=140.0, average=100.0),
        downlink_latency_ms=NumericMetricSummary(minimum=65.0, maximum=150.0, average=110.0),
    )

    summary = compare_analysis_summaries(baseline, candidate)

    assert summary.baseline_anomaly_rate == 0.2
    assert summary.candidate_anomaly_rate == 0.5
    assert summary.anomaly_rate_delta == 0.3
    assert summary.battery_pct_average.delta == -15.0
    assert summary.temperature_c_average.delta == 15.0
    assert summary.uplink_latency_ms_average.delta == 30.0
    assert summary.downlink_latency_ms_average.delta == 35.0