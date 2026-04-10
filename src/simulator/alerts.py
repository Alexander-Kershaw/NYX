from enum import Enum
from pydantic import BaseModel, Field


class AlertSeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    LOW_BATTERY = "low_battery"
    HIGH_TEMPERATURE = "high_temperature"
    LOW_TEMPERATURE = "low_temperature"
    HIGH_UPLINK_LATENCY = "high_uplink_latency"
    HIGH_DOWNLINK_LATENCY = "high_downlink_latency"
    WEAK_SIGNAL = "weak_signal"
    FAILED_AUTHENTICATION = "failed_auth"
    ANOMALY_FLAGGED = "anomaly_flagged"
    PACKET_INTEGRITY_DEGRADATION = "packet_integrity_degradation"
    SECURITY_BREACH = "security_breach"


class Alert(BaseModel):
    alert_id: str = Field(..., description="Unique alert identifier")
    event_id: str = Field(..., description="Telemetry event identifier that triggered the alert")
    event_timestamp: str = Field(..., description="Timestamp of the triggering telemetry event")
    satellite_id: str = Field(..., description="Satellite associated with the alert")
    event_type: str = Field(..., description="Telemetry event type that triggered the alert")
    alert_type: AlertType = Field(..., description="Type of alert raised")
    severity: AlertSeverityLevel = Field(..., description="Severity of the alert")
    message: str = Field(..., description="Human-readable alert message")
    anomaly_type: str | None = Field(default=None, description="Underlying anomaly type if present on the event")