from collections import Counter
from pathlib import Path

from simulator.io_utils import generate_summary_filepath
from simulator.simulation_summary import SimulationSummary, counter_to_dict


def test_counter_tor_dict_converts_counter() -> None:
    counter = Counter({"power": 2, "comms": 1})

    result = counter_to_dict(counter)

    assert result == {"power": 2, "comms": 1}


def test_generate_summary_filepath_returns_json_path(tmp_path: Path) -> None:
    summary_path = generate_summary_filepath(tmp_path, prefix="nyx_summary")

    assert summary_path.parent == tmp_path
    assert summary_path.name.startswith("nyx_summary_")
    assert summary_path.suffix == ".json"


def test_simulation_run_summary_model_accepts_expected_fields() -> None:
    summary = SimulationSummary(
        run_id="run-123",
        started_at="2026-04-09T05:30:00Z",
        finished_at="2026-04-09T05:30:05Z",
        total_events=10,
        anomaly_events=2,
        events_by_type={"heartbeat": 2, "navigation": 2},
        anomalies_by_type={"thermal_runaway": 1, "spoofed_source": 1},
        output_path="output/test.jsonl",
    )

    assert summary.total_events == 10
    assert summary.anomaly_events == 2
    assert summary.output_path == "output/test.jsonl"