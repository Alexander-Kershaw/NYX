from simulator.anomalies import anomalies_for_event_type, anomaly_choice_for_event_type, AnomalyType
from simulator.contracts import EventType


def test_anomalies_for_power_event() -> None:
    anomalies = anomalies_for_event_type(EventType.POWER)

    assert anomalies == [AnomalyType.BATTERY_DRAIN_SPIKE]


def test_anomalies_for_thermal_event() -> None:
    anomalies = anomalies_for_event_type(EventType.THERMAL)

    assert anomalies == [AnomalyType.THERMAL_RUNAWAY]


def test_anomalies_for_comms_event() -> None:
    anomalies = anomalies_for_event_type(EventType.COMMS)

    assert AnomalyType.SIGNAL_DEGRADATION in anomalies
    assert AnomalyType.SPOOFED_SOURCE in anomalies


def test_anomalies_for_navigation_event_is_empty() -> None:
    anomalies = anomalies_for_event_type(EventType.NAVIGATION)

    assert anomalies == []


def test_choose_anomaly_returns_none_for_unsupported_event_type() -> None:
    anomaly = anomaly_choice_for_event_type(EventType.HEARTBEAT, anomaly_rate=1.0)

    assert anomaly is None


def test_choose_anomaly_returns_supported_anomaly_when_rate_is_one() -> None:
    anomaly = anomaly_choice_for_event_type(EventType.POWER, anomaly_rate=1.0)

    assert anomaly == AnomalyType.BATTERY_DRAIN_SPIKE