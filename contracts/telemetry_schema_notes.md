***

# NYX Telemetry Event Schema Notes

***

## Purpose

This document defines the first draft of the telemetry event structure for NYX.

The telemetry schema will construct:
- the simulator output
- validation logic
- storage layout
- anomaly detection features
- analytics queries

## Core Design Principle

Each telemetry event should represent a single timestamped operational observation about a satellite and its communications status or system state.

### Candidate Telemetry Fields

- event_id
- event_timestamp
- satellite_id
- ground_station_id
- event_type
- latitude
- longitude
- altitude_km
- velocity_kms
- battery_pct
- temperature_c
- signal_strength_db
- uplink_latency_ms
- downlink_latency_ms
- packet_integrity_score
- auth_status
- source_ip
- payload_status

## Notes

These fields will probably be revised before any coding begins. The aim here is try and balance operational realism with implementation simplicity.

---