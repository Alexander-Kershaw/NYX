from pydantic import BaseModel, Field


class AlertRunSummary(BaseModel):
    telemetry_filepath: str = Field(..., description="Input NYX telemetry JSONL path")
    alert_output_filepath: str | None = Field(default=None, description="Output alert JSONL path if written")
    total_events_processed: int = Field(..., description="Number of telemetry events processed")
    total_alerts: int = Field(..., description="Number of alerts raised")
    alerts_by_type: dict[str, int] = Field(..., description="Alert counts grouped by type")
    alerts_by_severity: dict[str, int] = Field(..., description="Alert counts grouped by severity")