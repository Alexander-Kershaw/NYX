import argparse
import json

from simulator.analysis_output import analyze_jsonl_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a NYX telemetry output file")
    parser.add_argument("filepath", type=str, help="Path to the JSONL file to analyze")

    return parser.parse_args()


def main():
    arguments = parse_args()
    analysis_summary = analyze_jsonl_file(arguments.filepath)

    print("=====| NYX Telemetry Analysis Summary |=====")
    print(json.dumps(analysis_summary.model_dump(mode="json"), indent=2))

if __name__ == "__main__":
    main()

