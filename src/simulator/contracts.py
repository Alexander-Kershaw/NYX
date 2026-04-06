from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

"""
Defined a strict class structure using Enum (keeps values consistent) random strings cannot
be used for these fields so downstream everything is more clean / consistent, ensuring 
quality data and integrity.

The TelemetryEvent class is designed to capture a wide range of telemetry data from satellites,
every event will have a common set of fields (event_id, event_timestamp, satellite_id, etc.) and then
options for additional telemetry data that may not be present in every event (latitude, longitude, battery_pct, etc.).

pydantic parses the incoming data and validates it against the defined schema, rejects any invalid inputs,
and provides a clear error if the data does not conform to the schema I have enforced.
"""

class EventType(str, Enum):
    HEARTBEAT = "heartbeat"
    NAVIGATION = "navigation"
    POWER = "power"
    THERMAL = "thermal"
    COMMS = "comms"


class AuthStatus(str, Enum):
    AUTHENTICATED = "authenticated"
    FAILED = "failed"
    UNKNOWN = "unknown"


class PayloadStatus(str, Enum):
    NOMINAL = "nominal"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    SAFE_MODE = "safe_mode"


class MissionMode(str, Enum):
    NOMINAL = "nominal"
    STANDBY = "standby"
    SAFE = "safe"
    EMERGENCY = "emergency"


class OrbitClass(str, Enum):
    LEO = "LEO"
    MEO = "MEO"
    GEO = "GEO"


class TelemetryEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_timestamp: str = Field(..., description="Event timestamp in ISO 8601 format")
    satellite_id: str = Field(..., description="Satellite identifier")
    ground_station_id: str = Field(..., description="Ground station identifier")
    event_type: EventType = Field(..., description="Telemetry event type")
    schema_version: str = Field(..., description="Schema version")
    source_ip: str = Field(..., description="Source IP address")
    ingest_source: str = Field(..., description="Origin of the event, e.g. simulator")

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_km: Optional[float] = None
    velocity_kms: Optional[float] = None
    battery_pct: Optional[float] = None
    temperature_c: Optional[float] = None
    signal_strength_db: Optional[float] = None
    uplink_latency_ms: Optional[float] = None
    downlink_latency_ms: Optional[float] = None
    packet_integrity_score: Optional[float] = None
    auth_status: Optional[AuthStatus] = None
    payload_status: Optional[PayloadStatus] = None
    status_code: Optional[str] = None

    orbit_class: Optional[OrbitClass] = None
    mission_mode: Optional[MissionMode] = None
    is_anomalous: bool = False
    anomaly_type: Optional[str] = None


    # Validate fields are within the realistic ranges
    @field_validator("battery_pct")
    @classmethod
    def validate_battery_pct(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not 0 <= value <= 100:
            raise ValueError("battery_pct must be between 0 and 100")
        return value

    @field_validator("packet_integrity_score")
    @classmethod
    def validate_packet_integrity_score(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not 0 <= value <= 1:
            raise ValueError("packet_integrity_score must be between 0 and 1")
        return value

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return value


    # Validate that the required fields in the TelemetryEvent baseline model for each distict event type are present
    @model_validator(mode="after")
    def validate_event_type_requirements(self) -> "TelemetryEvent":
        event_type = self.event_type.value if isinstance(self.event_type, Enum) else str(self.event_type) # works for both str or Enum values

        required_by_type = {
            "navigation": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude_km": self.altitude_km,
                "velocity_kms": self.velocity_kms,
            },
            "power": {
                "battery_pct": self.battery_pct,
            },
            "thermal": {
                "temperature_c": self.temperature_c,
            },
            "comms": {
                "signal_strength_db": self.signal_strength_db,
                "uplink_latency_ms": self.uplink_latency_ms,
                "downlink_latency_ms": self.downlink_latency_ms,
                "packet_integrity_score": self.packet_integrity_score,
                "auth_status": self.auth_status,
            },
        }

        required_fields = required_by_type.get(event_type, {})
        missing_fields = [field_name for field_name, value in required_fields.items() if value is None]

        if missing_fields:
            missing_str = ", ".join(missing_fields)
            raise ValueError(f"{event_type} event is missing required field(s): {missing_str}")

        return self