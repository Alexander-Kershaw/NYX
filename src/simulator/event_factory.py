from datetime import UTC, datetime
from itertools import count
from random import choice, uniform

from simulator.assets import GROUND_STATIONS, SATELLITES, SOURCE_IPS
from simulator.contracts import AuthStatus, EventType, PayloadStatus, TelemetryEvent

# Incremental counter for generating unique event IDs
event_counter = count(1)

def generate_event_id() -> str:
    return f"event-{next(event_counter):06d}"

# UTC timestamp for event at generation time
def generate_event_timestamp() -> str:
    return datetime.now(UTC).isoformat()

# Choose between provided identifier for one from the known options defined in assets
def choose_identifier(provided: str | None, options: list[str]) -> str:
    return provided or choice(options)


def build_navigation_event(
    satellite_id: str | None = None,
    ground_station_id: str | None = None,
    source_ip: str | None = None,
) -> TelemetryEvent:
    satellite = choose_identifier(satellite_id, SATELLITES)
    ground_station = choose_identifier(ground_station_id, GROUND_STATIONS)
    ip_address = choose_identifier(source_ip, SOURCE_IPS)

    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=satellite,
        ground_station_id=ground_station,
        event_type=EventType.NAVIGATION,
        schema_version="1.0",
        source_ip=ip_address,
        ingest_source="simulator",
        latitude=uniform(-90.0, 90.0),
        longitude=uniform(-180.0, 180.0),
        altitude_km=uniform(500.0, 550.0),
        velocity_kms=uniform(7.5, 8.0),
        payload_status=PayloadStatus.NOMINAL,
    )


def build_heartbeat_event(
    satellite_id: str | None = None,
    ground_station_id: str | None = None,
    source_ip: str | None = None,
) -> TelemetryEvent:
    satellite = choose_identifier(satellite_id, SATELLITES)
    ground_station = choose_identifier(ground_station_id, GROUND_STATIONS)
    ip_address = choose_identifier(source_ip, SOURCE_IPS)

    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=satellite,
        ground_station_id=ground_station,
        event_type=EventType.HEARTBEAT,
        schema_version="1.0",
        source_ip=ip_address,
        ingest_source="simulator",
        payload_status=PayloadStatus.NOMINAL,
        status_code="OK",
    )


def build_power_event(
    satellite_id: str | None = None,
    ground_station_id: str | None = None,
    source_ip: str | None = None,
) -> TelemetryEvent:
    satellite = choose_identifier(satellite_id, SATELLITES)
    ground_station = choose_identifier(ground_station_id, GROUND_STATIONS)
    ip_address = choose_identifier(source_ip, SOURCE_IPS)

    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=satellite,
        ground_station_id=ground_station,
        event_type=EventType.POWER,
        schema_version="1.0",
        source_ip=ip_address,
        ingest_source="simulator",
        battery_pct=uniform(55.0, 100.0),
        payload_status=PayloadStatus.NOMINAL,
        status_code="PWR_OK",
    )


def build_thermal_event(
    satellite_id: str | None = None,
    ground_station_id: str | None = None,
    source_ip: str | None = None,
) -> TelemetryEvent:
    satellite = choose_identifier(satellite_id, SATELLITES)
    ground_station = choose_identifier(ground_station_id, GROUND_STATIONS)
    ip_address = choose_identifier(source_ip, SOURCE_IPS)

    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=satellite,
        ground_station_id=ground_station,
        event_type=EventType.THERMAL,
        schema_version="1.0",
        source_ip=ip_address,
        ingest_source="simulator",
        temperature_c=uniform(-20.0, 45.0),
        payload_status=PayloadStatus.NOMINAL,
        status_code="THERM_OK",
    )


def build_comms_event(
    satellite_id: str | None = None,
    ground_station_id: str | None = None,
    source_ip: str | None = None,
) -> TelemetryEvent:
    satellite = choose_identifier(satellite_id, SATELLITES)
    ground_station = choose_identifier(ground_station_id, GROUND_STATIONS)
    ip_address = choose_identifier(source_ip, SOURCE_IPS)

    return TelemetryEvent(
        event_id=generate_event_id(),
        event_timestamp=generate_event_timestamp(),
        satellite_id=satellite,
        ground_station_id=ground_station,
        event_type=EventType.COMMS,
        schema_version="1.0",
        source_ip=ip_address,
        ingest_source="simulator",
        signal_strength_db=uniform(-85.0, -60.0),
        uplink_latency_ms=uniform(40.0, 120.0),
        downlink_latency_ms=uniform(40.0, 120.0),
        packet_integrity_score=uniform(0.95, 1.0),
        auth_status=AuthStatus.AUTHENTICATED,
        payload_status=PayloadStatus.NOMINAL,
        status_code="COMMS_OK",
    )