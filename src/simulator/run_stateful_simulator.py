import argparse
import json
import time
from random import choice
from pathlib import Path
from collections import Counter
from datetime import UTC, datetime
from uuid import uuid4

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
    build_spoofing_event_from_state
)

from simulator.anomalies import apply_anomaly_to_state, anomaly_choice_for_event_type, AnomalyType
from simulator.io_utils import generate_output_filepath, generate_summary_filepath
from simulator.simulation_summary import SimulationSummary, counter_to_dict


# Runs a stateful simulator emitting telemetry based on evolving satellite event states (has memory of past events)
def run_stateful_simulator(
        iterations: int = 10,
        delay_seconds: float = 0.5,
        anomaly_rate: float = 0.2,
        output_path: Path | None = None,
        summary_path: Path | None = None
) -> SimulationSummary:
    
    states = initialize_satellite_states()

    event_cycle = [
        EventType.HEARTBEAT,
        EventType.NAVIGATION,
        EventType.POWER,
        EventType.THERMAL,
        EventType.COMMS,
    ]

    simulation_run_id = f"NYX_Simulator_Run-{uuid4()}"
    run_started_at = datetime.now(UTC).isoformat()

    events_by_type_counter: Counter[str] = Counter()
    anomalies_by_EventType_counter: Counter[str] = Counter()
    anomaly_events = 0

    output_file = None
    if output_path is not None:
        output_file = output_path.open("w", encoding="utf-8")


    print("=====| Starting NYX stateful simulator |=====")

    try:
        for index in range(iterations):
            satellite_id = choice(list(states.keys()))
            state = states[satellite_id]
            event_type = event_cycle[index % len(event_cycle)]
            anomaly_type = anomaly_choice_for_event_type(event_type, anomaly_rate)

            if anomaly_type is not None:
                apply_anomaly_to_state(state, anomaly_type)

            if event_type == EventType.HEARTBEAT:
                event = build_heartbeat_event_from_state(state, anomaly_type=anomaly_type)

            elif event_type == EventType.NAVIGATION:
                evolve_navigation(state)
                event = build_navigation_event_from_state(state, anomaly_type=anomaly_type)

            elif event_type == EventType.POWER:
                evolve_power(state)
                event = build_power_event_from_state(state, anomaly_type=anomaly_type)

            elif event_type == EventType.THERMAL:
                evolve_thermal(state)
                event = build_thermal_event_from_state(state, anomaly_type=anomaly_type)

            elif event_type == EventType.COMMS:
                evolve_comms(state)

                if anomaly_type == AnomalyType.SIGNAL_DEGRADATION:
                    event = build_comms_event_from_state(state, anomaly_type=anomaly_type)
                
                elif anomaly_type == AnomalyType.SPOOFED_SOURCE:
                    event = build_spoofing_event_from_state(state, anomaly_type=anomaly_type)

            else:
                raise ValueError(f"Unsupported event type: {event_type}")
            
            event_json_payload = json.dumps(event.model_dump(mode="json"))

            print(event_json_payload)

            if output_file is not None:
                output_file.write(event_json_payload + "\n")

            
            events_by_type_counter[event.event_type.value] += 1

            if event.is_anomalous:
                anomaly_events += 1
                if event.anomaly_type is not None:
                    anomalies_by_EventType_counter[event.anomaly_type] += 1

            time.sleep(delay_seconds)


    finally:
        if output_file is not None:
            output_file.close()

    run_finished_at = datetime.now(UTC).isoformat()

    run_summary = SimulationSummary(
        run_id = simulation_run_id,
        started_at = run_started_at,
        finished_at = run_finished_at,
        total_events = iterations,
        anomaly_events = anomaly_events,
        events_by_type = counter_to_dict(events_by_type_counter),
        anomalies_by_type = counter_to_dict(anomalies_by_EventType_counter),
        output_path = str(output_path) if output_path is not None else None
    )

    print("=====| NYX stateful simulator finished |=====")
    print("\n Saved NYX stateful simulator output to:", output_path if output_path is not None else "No output file (output_dir argument not provided)")

    print("\n =====| Simulation Run Summary |=====")
    print(json.dumps(run_summary.model_dump(mode="json"), indent=2))

    if summary_path is not None:
        with summary_path.open("w", encoding="utf-8") as summary_file:
            json.dump(run_summary.model_dump(mode="json"), summary_file, indent=2)
        
    return run_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the NYX stateful telemetry simulator")
    parser.add_argument("--iterations", type=int, default=10, help="Number of telemetry events to emit")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay in seconds between emitted events")
    parser.add_argument("--anomaly-rate", type=float, default=0.2, help="Probability of an anomaly occurring in an event")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to write emitted events as JSONL files")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    output_path = None
    summary_path = None

    if args.output_dir is not None:
        output_path = generate_output_filepath(args.output_dir, prefix="NYX_Stateful_Simulator_Output")
        summary_path = generate_summary_filepath(args.output_dir, prefix="NYX_Stateful_Simulator_Summary")

    run_stateful_simulator(
        iterations=args.iterations,
        delay_seconds=args.delay,
        anomaly_rate=args.anomaly_rate,
        output_path=output_path,
        summary_path=summary_path
    )