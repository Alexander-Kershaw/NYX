from itertools import count

from simulator.alerts import Alert, AlertSeverityLevel, AlertType
from simulator.contracts import AuthStatus, TelemetryEvent

alert_counter = count(1)


def generate_alert_id() -> str:
    return f"ALERT-{next(alert_counter):06d}"


def alert_from_telemetry_event(event: TelemetryEvent) -> list[Alert]:
    alerts: list[Alert] = []

    if event.battery_pct is not None and event.battery_pct < 30.0:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.LOW_BATTERY,
                severity=AlertSeverityLevel.HIGH,
                message=f"Battery level is low: {event.battery_pct:.2f}%"
                )
        )

    if event.temperature_c is not None and event.temperature_c > 70.0:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.HIGH_TEMPERATURE,
                severity=AlertSeverityLevel.HIGH,
                message=f"Temperature levels exceeding operational threshold: {event.temperature_c:.2f} C"
                )
        )
        
    if event.temperature_c is not None and event.temperature_c < -20.0:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.LOW_TEMPERATURE,
                severity=AlertSeverityLevel.HIGH,
                message=f"Temperature levels below operational threshold: {event.temperature_c:.2f} C"
                )
        )

    if event.uplink_latency_ms is not None and event.uplink_latency_ms > 500.0:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.HIGH_UPLINK_LATENCY,
                severity=AlertSeverityLevel.MEDIUM,
                message=f"Uplink latency is high: {event.uplink_latency_ms:.2f} ms"
                )
        )

    if event.downlink_latency_ms is not None and event.downlink_latency_ms > 500.0:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.HIGH_DOWNLINK_LATENCY,
                severity=AlertSeverityLevel.MEDIUM,
                message=f"Downlink latency is high: {event.downlink_latency_ms:.2f} ms"
                )
        )

    if event.signal_strength_db is not None and event.signal_strength_db < -100.0:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.WEAK_SIGNAL,
                severity=AlertSeverityLevel.MEDIUM,
                message=f"Signal strength is weak: {event.signal_strength_db:.2f} dB"
                )
        )

    if event.auth_status == AuthStatus.FAILED:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.FAILED_AUTHENTICATION,
                severity=AlertSeverityLevel.CRITICAL,
                message="Authentication failure detected"
                )
        )

    if event.anomaly_type is not None:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.ANOMALY_FLAGGED,
                severity=AlertSeverityLevel.HIGH,
                message=f"Anomaly detected: {event.anomaly_type}"
                )
        )

    if event.packet_integrity_score is not None and event.packet_integrity_score < 0.95:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.PACKET_INTEGRITY_DEGRADATION,
                severity=AlertSeverityLevel.MEDIUM,
                message=f"Packet integrity degradation detected: {event.packet_integrity_score:.2%}"
                )
        )

    if event.auth_status == AuthStatus.FAILED or AuthStatus.UNKNOWN and event.anomaly_type is not None and event.packet_integrity_score is not None and event.packet_integrity_score < 0.95:
        alerts.append(
            build_alert(
                event=event,
                alert_type=AlertType.SECURITY_BREACH,
                severity=AlertSeverityLevel.CRITICAL,
                message="Potential security breach detected: Failed authentication, anomaly flagged, and packet integrity degradation"
                )
        )

    return alerts
    


def build_alert(event: TelemetryEvent,
                alert_type: AlertType,
                severity: AlertSeverityLevel,
                message: str) -> Alert:
    return Alert(
        alert_id=generate_alert_id(),
        event_id=event.event_id,
        event_timestamp=event.event_timestamp,
        satellite_id=event.satellite_id,
        event_type=event.event_type.value,
        alert_type=alert_type,
        severity=severity,
        message=message,
        anomaly_type=event.anomaly_type
    )

