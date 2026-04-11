import json
import os
from pathlib import Path

from cloud.lambda_consumer import lambda_handler

# Not executing this script as local run, testing via pytest

def main() -> None:
    lambda_test_path = Path("src/cloud/test_lambda_consumer_event.json")

    with lambda_test_path.open("r", encoding="utf-8") as test_file:
        event = json.load(test_file)

    # For local invocation of the lambda function using some dummy environment variables
    os.environ["NYX_BRONZE_BUCKET"] = "dummy-local-bucket"
    os.environ["NYX_BRONZE_PREFIX"] = "bronze/telemetry"

    result = lambda_handler(event, context=None)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

    