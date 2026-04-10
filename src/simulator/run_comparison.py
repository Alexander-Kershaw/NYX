import argparse
import json

from simulator.compare_runs import compare_jsonl_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two NYX telemetry JSONL output files")
    parser.add_argument("baseline_filepath", type=str, help="Path to the baseline JSONL file")
    parser.add_argument("candidate_filepath", type=str, help="Path to the candidate JSONL file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = compare_jsonl_files(baseline_filepath=args.baseline_filepath, candidate_filepath=args.candidate_filepath)

    print("=== NYX telemetry comparison summary ===")
    print(json.dumps(summary.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()