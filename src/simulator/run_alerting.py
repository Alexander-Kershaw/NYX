import argparse
import json
from pathlib import Path

from simulator.generate_alerts import generate_alerts_from_telemetry_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate alerts from a NYX telemetry JSONL output file"
    )
    parser.add_argument("telemetry_filepath", type=str, help="Path to the NYX telemetry JSONL file")
    parser.add_argument("--alert_output", type=str, default=None, help="Optional Path to write the generate alerts as JSONL")

    return parser.parse_args()


def main() -> None:
    arguments = parse_args()

    alerts_summary = generate_alerts_from_telemetry_jsonl(
        telemetry_filepath=Path(arguments.telemetry_filepath),
        alert_summary_output_path=Path(arguments.alert_output) if arguments.alert_output else None,
    )

    print("=====| NYX Alert Generation Summary |=====")
    print(json.dumps(alerts_summary.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()