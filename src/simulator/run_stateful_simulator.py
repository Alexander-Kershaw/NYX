import argparse
import json
import time
from random import choice

from simulator.contracts import EventType
from simulator.state_manager import (
    evolve_comms,
    evolve_navigation,
    evolve_power,
    evolve_thermal,
    initialize_satellite_states,
)

from simulator.stateful_event_factory import (
    build_comms_event_from_state,
    build_heartbeat_event_from_state,
    build_navigation_event_from_state,
    build_power_event_from_state,
    build_thermal_event_from_state,
)

# Runs a stateful simulator emitting telemetry based on evolving satellite event states (has memory of past events)
def run_stateful_simulator(iterations: int = 10, delay_seconds: float = 0.5) -> None:
    states = initialize_satellite_states()

    event_cycle = [
        EventType.HEARTBEAT,
        EventType.NAVIGATION,
        EventType.POWER,
        EventType.THERMAL,
        EventType.COMMS,
    ]

    print("=====| Starting NYX stateful simulator |=====")

    for index in range(iterations):
        satellite_id = choice(list(states.keys()))
        state = states[satellite_id]
        event_type = event_cycle[index % len(event_cycle)]

        if event_type == EventType.HEARTBEAT:
            event = build_heartbeat_event_from_state(state)

        elif event_type == EventType.NAVIGATION:
            evolve_navigation(state)
            event = build_navigation_event_from_state(state)

        elif event_type == EventType.POWER:
            evolve_power(state)
            event = build_power_event_from_state(state)

        elif event_type == EventType.THERMAL:
            evolve_thermal(state)
            event = build_thermal_event_from_state(state)

        elif event_type == EventType.COMMS:
            evolve_comms(state)
            event = build_comms_event_from_state(state)

        else:
            raise ValueError(f"Unsupported event type: {event_type}")

        print(json.dumps(event.model_dump(mode="json")))
        time.sleep(delay_seconds)

    print("=====| NYX stateful simulator finished |=====")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the NYX stateful telemetry simulator")
    parser.add_argument("--iterations", type=int, default=10, help="Number of telemetry events to emit")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between emitted events")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_stateful_simulator(iterations=args.iterations, delay_seconds=args.delay)