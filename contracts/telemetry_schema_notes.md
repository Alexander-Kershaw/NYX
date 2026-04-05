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

## Core Entities

Satellite telemetry events contain a plethora of information regarding different functional and operational factors of the satellites within the consetllation. I decided to define a telemetry event as a discrete timestamped report from the satellite detailing the specifics of its operational state or communication condition either directly or through a station on the ground.

Therefore, the event is basically a singular observation at one moment in time. This would be better for NYX data to be cleaner rather than a massive bundle of unrelated information. 

The philosophy for the telemetry event design is such that its small enough to effectively process (no cumbersome and bloated nested data), informationally rich enough to perform worthwhile analysis (enough for contract validation, anomaly detection and SQL analytics downstream), A decent degree of operational realism, and consistent enough for explicit definitions of data contracts (same shape and predictable meaning).

I decided to categorise information into the following:

### Satellite
The primary monitored asset in the system. Each satellite emits telemetry events describing key aspects of its operational state.

### Ground Station
A receiving or relaying station that interacts with a satellite and provides communications context for telemetry.

### Telemetry Event
A single timestamped observation about a satellite's state, communication health, or subsystem condition.

### Alert
A derived system output generated when telemetry matches suspicious or anomalous patterns.

## Initial Event Types

- heartbeat
- navigation
- power
- thermal
- comms

## Event Type Meanings

### heartbeat
Represents a basic operational pulse confirming the satellite is alive and operational.

### navigation
Represents the satellite's motion and position state in space.

### power
Represents power system health, including battery-related status.

### thermal
Represents thermal system state and temperature health.

### comms
Represents communication link quality, latency, integrity, and authentication state.

## Initial Simulated Assets

### Satellites

Just a generic naming system representing a satellite in the constellation. I am keeping it a small system initially.

- NYX-SAT-001
- NYX-SAT-002
- NYX-SAT-003

### Ground Stations

Another set of generic ground stations completing the communication link from ground to satellite. Also keeping this small for now.

- GND-UK-001
- GND-NO-001

## Initial Anomaly Categories

- operational anomalies
- navigation anomalies
- communications anomalies
- security adjacent anomalies

---

