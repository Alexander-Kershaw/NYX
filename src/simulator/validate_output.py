import argparse 
import json

from simulator.reader import validate_telemetry_jsonl

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a NYX telemetry JSONL file and summarize the results.")
    parser.add_argument("filepath", type=str, help="Path to the telemetry JSONL file to validate")
    
    return parser.parse_args()

def main():
    args = parse_args()
    validation_summary = validate_telemetry_jsonl(args.filepath)
    
    print("=====| NYX Telemetry Validation Summary |=====")
    print(json.dumps(validation_summary.model_dump(mode="json"), indent=2))

if __name__ == "__main__":
    main()