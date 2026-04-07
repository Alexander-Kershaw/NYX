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

## Field-Level Schema Design

I decided that NYX will use a unified telemetry event schema.

This means every telemetry record will share a common consistent event structure, while some fields will only be populated for relevant event types (so some fields may be null depending on the type of event). This approach simplifies ingestion, validation, storage, and analytics while still allowing event specific meaning.

A single telemetry schema allows for a single ingestion path, singular validation contract, one bronze format, one silver transformation model, and a single table shape that I could SQL query with Athena donwstream.

The schema structure can be divided into four subgroups:

- Event identity and metadata (the who, what, when, etc....)
- Context Fields (Where the event originates from and what satallite operational subsystem is refers to)
- Telemetry measurement fields (Actual measurements such as communications signal, temperature, etc...)
- Security and trust fields (Is the actual information trustworthy or compromised)

## Required Common Fields

These fields exist for every telemetry event as default

| Field               | Type              | Why it exists                                    |
| ------------------- | ----------------- | ------------------------------------------------ |
| `event_id`          | string            | unique identifier for traceability               |
| `event_timestamp`   | string (ISO 8601) | when the event occurred                          |
| `satellite_id`      | string            | which satellite emitted the event                |
| `ground_station_id` | string            | receiving or relaying station                    |
| `event_type`        | string            | heartbeat / navigation / power / thermal / comms |
| `schema_version`    | string            | future-proofing the contract                     |
| `source_ip`         | string            | source identity context                          |
| `ingest_source`     | string            | simulator, replay, test harness, etc.            |


## Optional Measurement Fields

The optional fields are relevent depending on the event type

| Field                    | Type   | Used by                             |
| ------------------------ | ------ | ----------------------------------- |
| `latitude`               | float  | navigation                          |
| `longitude`              | float  | navigation                          |
| `altitude_km`            | float  | navigation                          |
| `velocity_kms`           | float  | navigation                          |
| `battery_pct`            | float  | power                               |
| `temperature_c`          | float  | thermal                             |
| `signal_strength_db`     | float  | comms                               |
| `uplink_latency_ms`      | float  | comms                               |
| `downlink_latency_ms`    | float  | comms                               |
| `packet_integrity_score` | float  | comms                               |
| `auth_status`            | string | comms / security                    |
| `payload_status`         | string | heartbeat / power / thermal / comms |
| `status_code`            | string | generic subsystem status            |


## Optional Context Fields

These context fields exist as additional add ons that improve realism for satellite operations and also is for future anamolous event injection later in the project.

| Field          | Type    | Why                                              |
| -------------- | ------- | ------------------------------------------------ |
| `orbit_class`  | string  | LEO/MEO/GEO style context                        |
| `mission_mode` | string  | nominal, standby, safe, emergency                |
| `is_anomalous` | boolean | useful in simulator labelled training/evaluation |
| `anomaly_type` | string  | what anomaly was injected, if any                |

## Conditional Requirements by Event Type

### heartbeat
Typically lightweight. May include payload_status and status_code.

### navigation
Should include:
- latitude
- longitude
- altitude_km
- velocity_kms

### power
Should include:
- battery_pct

### thermal
Should include:
- temperature_c

### comms
Should include:
- signal_strength_db
- uplink_latency_ms
- downlink_latency_ms
- packet_integrity_score
- auth_status

## Allowed Values

### event_type
- heartbeat
- navigation
- power
- thermal
- comms

### auth_status
- authenticated
- failed
- unknown

### payload_status
- nominal
- degraded
- offline
- safe_mode

### mission_mode
- nominal
- standby
- safe
- emergency

### orbit_class
- LEO
- MEO
- GEO

## Validation Philosophy

The schema should validate:
- required field presence
- allowed values for categorical fields
- numeric range sanity
- conditional field requirements based on event_type

Optional fields may be null when they are not relevant to the event type, but should not contain invalid values when populated.

## Design Rationale

A unified flat schema is preferred for the first version of NYX because it simplifies:
- simulator implementation
- validation logic
- bronze and silver storage design
- Athena SQL querying
- downstream anomaly detection and analytics

---

## Anomaly Catalogue

Since I intend that NYX will simulate and detect a focused set of anomaly scenarios representing operational faults, navigation inconsistencies, communications degradation, and security suspicious behaviour, an anomaly catalogue is necessary.

The purpose of the anomaly catalogue is to:
- guide the telemetry simulation
- define some realistic failure, faults, and threat scenarios
- support rule based anomaly detection detection
- support future machine learning based anomaly scoring (hybrid with rule based as a complete detection system)
- improve the realism and explainability of the platform

The anomaly catalogue is essentially a structured list of information that characterises a threat such as: the name of the anomaly, what the anomaly means, what fields (satellite operational subsystems / security) the impact, whether they are operational or security related threats or failures, how sever they are in thier impact, how detectable they should be.

---

## Anomaly Families

I considered 4 distict families of anomalies.

I decided on this structure since it could map to simulator anomaly injections, validation rules, ML features, and dashboard categories quite naturally.

### Operational anomalies
Internal health or subsystem issues such as abnormal battery or thermal behaviour.

### Navigation anomalies
Movement or positional patterns that are implausible or inconsistent with expected orbital trajectory and continuity.

### Communications anomalies
Degraded telecommunications quality, latency problems, or transmission integrity issues.

### Security anomalies
Suspicious origin, identity, replay, or trust-related telemetry patterns. These are events that suggest spoofing and tampering.

---

## Initial Anomaly Set

I am initially starting with a set of 8 anomalies that represent some potential injections in the telemetry simulator. I defined that event family that the anomaly is associated with, the meaning for intuition, the fields likely to be impacted by the injection event, and a severity category.

For example a battery level could fall from 78% to 51% in an implausibly short interval, impacting the operational integrity family of telemetry events, impacting some relevant fields within that family (such as battery_pct, payload_status, etc...), yielding a severity (low, medium, high).

### battery_drain_spike
- Family: operational
- Meaning: battery level drops faster than expected over a short interval
- Likely affected fields: battery_pct, payload_status, status_code
- Initial severity: medium

This could indicate a power subsystem fault, power leakage, unexpected stress (potentially attack induced), to be detected with a set of rules first, then later ML can learn patterns for this sort of anomaly.

### thermal_runaway
- Family: operational
- Meaning: temperature rises above expected safe operating conditions
- Likely affected fields: temperature_c, payload_status, status_code
- Initial severity: high

Incidates potential hardware faults, cooling failures, hostile conditions, excessive activity, and may be detected with a temperature threhsold rule, a trend-based rule, and ML later.

### signal_degradation
- Family: communications
- Meaning: signal strength falls below expected operational quality
- Likely affected fields: signal_strength_db, uplink_latency_ms, downlink_latency_ms, payload_status
- Initial severity: medium

Could represent environmental interference such as attenuation or obstruction, antenna mechanical or technical failure, hostile jamming, and could be detected using a threshold rule or a repetition event rule.

### latency_spike
- Family: communications
- Meaning: uplink or downlink latency rises well above nominal levels
- Likely affected fields: uplink_latency_ms, downlink_latency_ms, packet_integrity_score
- Initial severity: medium

This may be indicative of telecommunication congestion, a routing issue, link degradation, malicious interference, could be detected using a threshold rule, and potentially a rolling baseline ML model later.

### packet_corruption
- Family: communications
- Meaning: packet integrity score falls below trusted levels
- Likely affected fields: packet_integrity_score, payload_status, status_code
- Initial severity: medium

Could represent a noisy link, corruption in transit, malformed transmission, security risk such as tampering, detected using a rule based definition.

### impossible_position_jump
- Family: navigation
- Meaning: the reported movement between events is implausible for the satellite
- Likely affected fields: latitude, longitude, altitude_km, velocity_kms
- Initial severity: high

May indicate navigational faults, corruptions in telemetry, telemetry instrumentation failure / miscalibration, data spoofing, replay mismatching, detected using a stateful rule and / or a temporal consistency check.

Note this means that multiple telemetry events are considered not just anomalies within the same row to check the temporal consistency of telemetry.

### spoofed_source
- Family: security
- Meaning: telemetry appears to come from an untrusted or unexpected source
- Likely affected fields: source_ip, auth_status, ground_station_id, status_code
- Initial severity: high

Indication of identity forgery, malicious injection attack, or a compromised communications pathway. This may be detected using a strict allowlist rule and / or a failed identify authentication rule.

### replay_pattern
- Family: security
- Meaning: events or event sequences appear duplicated or reused in a suspicious way
- Likely affected fields: event_timestamp, event_id, satellite_id, repeated telemetry values
- Initial severity: high

Represents a replay attack, faults in the telemetry simulation, or an upstream duplication bug, this could be addressed with a duplicate pattern rule and temporal sequence analysis.

---

## Severity Model

So far I have decided on the following initial severity list:

| Anomaly                  | Severity |
| ------------------------ | -------- |
| battery_drain_spike      | medium   |
| thermal_runaway          | high     |
| signal_degradation       | medium   |
| latency_spike            | medium   |
| packet_corruption        | medium   |
| impossible_position_jump | high     |
| spoofed_source           | high     |
| replay_pattern           | high     |

A `critial` field could also be implemented with compounding issues such as: spoofed source, in conjunction with failed authentication and a corrputed packet is a **critial** severity.

This layered compounding severity logic could be added later.

---

## Detection Philosophy

NYX will use a hybrid detection approach using a mix of deterministic rules and ML detections.

### Rules-based detection
Used for clearly defined conditions such as:
- impossible values
- threshold breaches
- failed authentication
- untrusted source identities
- repeated or duplicated patterns

### ML-based anomaly detection
Planned for future phases to help identify:
- more subtle deviations from the norm
- combinations of weak signals
- behaviour that is unusual relative to recent baseline patterns

## Simulation Philosophy

The simulator should eventually generate both:
- Conspicuous anomalies that are easy to detect and classify
- subtle anomalies that are closer to realistic operational drift or suspicious weak signals

This helps make the platform more realistic and gives the later detection layer a stronger purpose.

---

## Implementation Note

The first executable version of the telemetry contract is implemented as a Pydantic model.

This contract currently enforces:
- required common fields universal to all event types
- allowed categorical values via enums
- numeric sanity checks for selected fields
- conditional required fields based on specific event types

This allows the simulator and later ingestion stages to validate telemetry consistently before writing data downstream.

---