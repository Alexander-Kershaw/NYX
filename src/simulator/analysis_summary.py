from pydantic import BaseModel, Field


class NumericMetricSummary(BaseModel):
    minimum: float | None = Field(default=None, description="Minimum observed value")
    maximum: float | None = Field(default=None, description="Maximum observed value")
    average: float | None = Field(default=None, description="Average observed value")


class TelemetryAnalysisSummary(BaseModel):
    filepath: str = Field(..., description="Path to the analyzed JSONL file")
    total_valid_events: int = Field(..., description="Total number of valid events analyzed")
    anomaly_events: int = Field(..., description="Number of anomalous valid events")
    anomaly_rate: float = Field(..., description="Proportion of valid events marked anomalous")
    events_by_type: dict[str, int] = Field(..., description="Counts of valid events grouped by event type")
    anomalies_by_type: dict[str, int] = Field(..., description="Counts of anomalous events grouped by anomaly type")
    battery_pct: NumericMetricSummary = Field(..., description="Summary statistics for battery percentage")
    temperature_c: NumericMetricSummary = Field(..., description="Summary statistics for temperature")
    uplink_latency_ms: NumericMetricSummary = Field(..., description="Summary statistics for uplink latency")
    downlink_latency_ms: NumericMetricSummary = Field(..., description="Summary statistics for downlink latency")