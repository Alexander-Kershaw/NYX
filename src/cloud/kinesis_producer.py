import argparse
import json
import logging
from collections.abc import Callable

import boto3

from simulator.contracts import TelemetryEvent
from simulator.event_factory import (
    build_comms_event,
    build_heartbeat_event,
    build_navigation_event,
    build_power_event,
    build_thermal_event
)

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


EventFactory = Callable[[], TelemetryEvent]

def build_event_factory_cycle() -> list[EventFactory]:
    return [
        build_heartbeat_event,
        build_navigation_event,
        build_power_event,
        build_thermal_event,
        build_comms_event
    ]


def send_event_to_kinesis(*, client: boto3.client, stream_name: str, event: TelemetryEvent) -> dict:
    
    telemetry_payload = json.dumps(event.model_dump(mode="json"))
    partition_key = event.satellite_id

    response = client.put_record(
        StreamName=stream_name,
        Data=telemetry_payload.encode("utf-8"),
        PartitionKey=partition_key
    )

    LOGGER.info(
        "Sent event_id=%s satellite_id=%s event_type=%s to stream=%s",
        event.event_id,
        event.satellite_id,
        event.event_type.value,
        stream_name
    )

    return response


def produce_events(*, stream_name: str, count: int, region: str) -> None:

    kinesis_client = boto3.client("kinesis", region_name=region)
    event_factories = build_event_factory_cycle()

    LOGGER.info("Producing %s telemetry events to Kinesis stream %s", count, stream_name)

    for i in range(count):
        event_factory = event_factories[i % len(event_factories)]
        event = event_factory()
        send_event_to_kinesis(
            client=kinesis_client,
            stream_name=stream_name,
            event=event
        )

    LOGGER.info("Finished producing %s events", count)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send NYX satellite telemetry events to Kinesis")

    parser.add_argument("--stream_name", type=str, required=True, help="Target Kinesis stream name")
    parser.add_argument("--count", type=int, default=10, help="Number of telemetry events to send")
    parser.add_argument("--region", type=str, default="eu-west-2", help="AWS region for the Kinesis stream")

    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    produce_events(
        stream_name=arguments.stream_name,
        count=arguments.count,
        region=arguments.region
    )
    