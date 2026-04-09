from collections import Counter
from pathlib import Path

from pydantic import BaseModel, Field

class SimulationSummary(BaseModel):
    run_id: str = Field(..., description="Unique identifier for the simulator run")
    started_at: str = Field(..., description="UTC timestamp when the run started")
    finished_at: str = Field(..., description="UTC timestamp when the run finished")
    total_events: int = Field(..., description="Total number of events emitted")
    anomaly_events: int = Field(..., description="Number of anomalous events emitted")
    events_by_type: dict[str, int] = Field(
        ..., description="Counts of emitted events grouped by event type"
    )
    anomalies_by_type: dict[str, int] = Field(
        ..., description="Counts of anomalies grouped by anomaly type"
    )
    output_path: str | None = Field(
        default=None, description="Path to the emitted JSONL file if persisted"
    )


def empty_counter_dict() -> Counter[str]:
    return Counter()


def counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(counter)