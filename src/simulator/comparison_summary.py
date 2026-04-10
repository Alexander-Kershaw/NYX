from pydantic import BaseModel, Field


class MetricDeltaSummary(BaseModel):
    baseline: float | None = Field(default=None, description="Baseline metric value")
    candidate: float | None = Field(default=None, description="Candidate metric value")
    delta: float | None = Field(default=None, description="Candidate minus baseline")


class TelemetryComparisonSummary(BaseModel):
    baseline_filepath: str = Field(..., description="Path to the baseline JSONL file")
    candidate_filepath: str = Field(..., description="Path to the candidate JSONL file")

    baseline_total_valid_events: int = Field(..., description="Baseline valid event count")
    candidate_total_valid_events: int = Field(..., description="Candidate valid event count")

    baseline_anomaly_events: int = Field(..., description="Baseline anomaly event count")
    candidate_anomaly_events: int = Field(..., description="Candidate anomaly event count")

    baseline_anomaly_rate: float = Field(..., description="Baseline anomaly rate")
    candidate_anomaly_rate: float = Field(..., description="Candidate anomaly rate")
    anomaly_rate_delta: float = Field(..., description="Candidate anomaly rate minus baseline anomaly rate")

    baseline_events_by_type: dict[str, int] = Field(..., description="Baseline event counts by type")
    candidate_events_by_type: dict[str, int] = Field(..., description="Candidate event counts by type")

    baseline_anomalies_by_type: dict[str, int] = Field(..., description="Baseline anomaly counts by type")
    candidate_anomalies_by_type: dict[str, int] = Field(..., description="Candidate anomaly counts by type")

    battery_pct_average: MetricDeltaSummary = Field(..., description="Battery average comparison")
    temperature_c_average: MetricDeltaSummary = Field(..., description="Temperature average comparison")
    uplink_latency_ms_average: MetricDeltaSummary = Field(..., description="Uplink latency average comparison")
    downlink_latency_ms_average: MetricDeltaSummary = Field(..., description="Downlink latency average comparison")