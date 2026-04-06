from simulator.event_factory import (
    build_comms_event,
    build_heartbeat_event,
    build_navigation_event,
    build_power_event,
    build_thermal_event,
)


def main() -> None:
    print("=== NYX generated telemetry events ===")

    events = [
        build_heartbeat_event(),
        build_navigation_event(),
        build_power_event(),
        build_thermal_event(),
        build_comms_event(),
    ]

    for event in events:
        print(event.model_dump(mode="json"))


if __name__ == "__main__":
    main()