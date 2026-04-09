from simulator.anomalies import AnomalyType, apply_anomaly_to_state
from simulator.state_manager import initialize_satellite_states
from simulator.stateful_event_factory import (
    build_spoofing_event_from_state,
    build_power_event_from_state,
    build_thermal_event_from_state,
    build_comms_degradation_event_from_state
)

def main() -> None:
    states = initialize_satellite_states()
    state = states["NYX-SAT-001"]

    print("=====| Nominal power event |=====")
    print(build_power_event_from_state(state).model_dump(mode="json"))

    apply_anomaly_to_state(state, AnomalyType.BATTERY_DRAIN_SPIKE)
    print("\n=====| Battery drain anomaly |=====")
    print(build_power_event_from_state(state, anomaly_type=AnomalyType.BATTERY_DRAIN_SPIKE).model_dump(mode="json"))

    print("\n=====| Nominal thermal event |=====")
    print(build_thermal_event_from_state(state).model_dump(mode="json"))

    apply_anomaly_to_state(state, AnomalyType.THERMAL_RUNAWAY)
    print("\n=====| Thermal runaway anomaly |=====")
    print(build_thermal_event_from_state(state, anomaly_type=AnomalyType.THERMAL_RUNAWAY).model_dump(mode="json"))

    print("\n=====| Nominal comms event (pre spoofing) |=====")
    print(build_spoofing_event_from_state(state).model_dump(mode="json"))

    apply_anomaly_to_state(state, AnomalyType.SPOOFED_SOURCE)
    print("\n=====| Spoofed comms anomaly |=====")
    print(build_spoofing_event_from_state(state, anomaly_type=AnomalyType.SPOOFED_SOURCE).model_dump(mode="json"))

    print("\n=====| Nominal comms event (signal degradation case)|=====")
    print(build_comms_degradation_event_from_state(state).model_dump(mode="json"))

    apply_anomaly_to_state(state, AnomalyType.SIGNAL_DEGRADATION)
    print("\n=====| Signal degradation event |=====")
    print(build_comms_degradation_event_from_state(state, anomaly_type=AnomalyType.SIGNAL_DEGRADATION).model_dump(mode="json"))

if __name__ == "__main__":
    main()