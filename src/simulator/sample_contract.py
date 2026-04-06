from simulator.contracts import TelemetryEvent, EventType, PayloadStatus


event = TelemetryEvent(
    event_id="evt-000001",
    event_timestamp="2026-04-06T10:15:00Z",
    satellite_id="NYX-SAT-001",
    ground_station_id="GND-UK-001",
    event_type=EventType.NAVIGATION,
    schema_version="1.0",
    source_ip="192.168.1.10",
    ingest_source="simulator",
    latitude=51.5074,
    longitude=-0.1278,
    altitude_km=540.2,
    velocity_kms=7.66,
    payload_status=PayloadStatus.NOMINAL,
)

print(event.model_dump())