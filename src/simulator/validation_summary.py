from pydantic import BaseModel, Field

class TelemetryValidationSummary(BaseModel):
    filepath: str = Field(..., description="Path to the JSONL file that was validated")
    total_records: int = Field(..., description="Total number of records read")
    valid_records: int = Field(..., description="Number of records that passed validation")
    invalid_records: int = Field(..., description="Number of records that failed validation")
    events_by_type: dict[str, int] = Field(
        ..., description="Counts of valid events grouped by event type"
    )
    anomalies_by_type: dict[str, int] = Field(
        ..., description="Counts of anomalous events grouped by anomaly type"
    )
    invalid_sample: list[str] = Field(default_factory=list,
        description="A few sample validation error messages",
    )