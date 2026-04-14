import json
import logging
import boto3

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def build_invalid_event() -> dict:

    return {
        "event_id": "evt-invalid-0001",
        "event_timestamp": "2026-04-11T12:00:00Z",
        "satellite_id": "NYX-SAT-001",
        "ground_station_id": "GND-UK-001",
        "event_type": "power",
        "schema_version": "1.0",
        "source_ip": "192.168.1.10",
        "ingest_source": "simulator",
        "battery_pct": 150.0,  # Invalid battery percentage
        "payload_status": "nominal",
        "status_code": "PWR_OK",
        "is_anomalous": False,
        "anomaly_type": None,
    }


def send_invalid_event_to_kinesis(*, stream_name: str, region: str) -> None:
    kinesis_client = boto3.client("kinesis", region_name=region)

    event = build_invalid_event()

    response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=json.dumps(event).encode("utf-8"),
        PartitionKey=event["satellite_id"]
    )

    LOGGER.info("Sent INVALID event to stream %s", stream_name)
    LOGGER.info("Kinesis response: %s", response)


if __name__ == "__main__":
    send_invalid_event_to_kinesis(stream_name="nyx-telemetry-stream", region="eu-west-2")

