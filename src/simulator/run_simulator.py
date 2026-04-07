import json
import time
import argparse
from collections.abc import Callable

from simulator.contracts import TelemetryEvent
from simulator.event_factory import (
    build_comms_event,
    build_heartbeat_event,
    build_navigation_event,
    build_power_event,
    build_thermal_event
)

EventFactory = Callable[[], TelemetryEvent]

# Returns the list of event factory functions used to generate a stream of telemetry events.
def create_event_factories() -> list[EventFactory]:
    return [
        build_comms_event,
        build_heartbeat_event,
        build_navigation_event,
        build_power_event,
        build_thermal_event
    ]

# Run the telemetry simulator (cycle through event factories) with number of iterations and delay between each distinct event.
def run_simulator(iterations: int = 10, delay_seconds: float = 0.5) -> None:
    event_factories = create_event_factories()

    print("=====| Starting NYX Satellite Telemetry Simulator |=====")
    print(f"Generating {iterations} iterations of telemetry events with a delay of {delay_seconds} seconds between each event.\n")

    for i in range(iterations):
        event_factory = event_factories[i % len(event_factories)]
        event = event_factory()

        print(json.dumps(event.model_dump(mode="json")))
        time.sleep(delay_seconds)

    print("\n=====| Simulation Complete |=====")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description= "Run NYX Satellite Telemetry Simulator")
    parser.add_argument("--iterations", type=int, default=10, help="Number of telemetry events to generate")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between generating each telemetry event")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    run_simulator(iterations=arguments.iterations, delay_seconds=arguments.delay)