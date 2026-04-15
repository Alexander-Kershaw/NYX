import json
import logging
import boto3

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Event is valid but triggers the SNS alerting
def build_alert_trigger_event() -> dict:

    return {
        "event_id": "evt-alert-0001",
        "event_timestamp": "2026-04-11T18:00:00Z",
        "satellite_id": "NYX-SAT-001",
        "ground_station_id": "GND-UK-001",
        "event_type": "comms",
        "schema_version": "1.0",
        "source_ip": "203.0.113.250",
        "ingest_source": "simulator",
        "signal_strength_db": -102.0,
        "uplink_latency_ms": 320.0,
        "downlink_latency_ms": 345.0,
        "packet_integrity_score": 0.45,
        "auth_status": "failed",
        "payload_status": "degraded",
        "status_code": "COMMS_WARN",
        "orbit_class": "LEO",
        "mission_mode": "nominal",
        "is_anomalous": True,
        "anomaly_type": "spoofed_source",
    }


def send_alert_trigger_event(*, stream_name: str, region: str) -> None:
    client = boto3.client("kinesis", region_name=region)
    
    event = build_alert_trigger_event()
    payload = json.dumps(event)

    response = client.put_record(StreamName=stream_name, Data=payload.encode("utf-8"), PartitionKey=event["satellite_id"])

    LOGGER.info("Sent valid alert triggering event to stream %s", stream_name)
    LOGGER.info("Kinesis response: %s", response)


if __name__ == "__main__":
    send_alert_trigger_event(stream_name="nyx-telemetry-stream", region="eu-west-2")