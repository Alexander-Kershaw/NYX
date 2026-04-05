***

# DEVLOG - NYX

***

## Entry 001 - Project Initialisation (Sunday 5th April 2026)

### What I did
- Created the initial repository structure
- Defined the initial project summary in the README
- Started a DEVLOG to record design decisions and implementation progression
- Started planning the satellite telemetry schema and some anomaly scenarios

### Why I did it
Before building any AWS cloud infrastructure or writing any satellite simulator code, I wanted to define the project shape, objectives, the potential milestones. This reduces rework later and makes the project easier to intuitively understand the project as well as test, and document it.

### What I learned
A strong engineering project should begin with clear definitions of system boundaries, data expectations, and documentation forsight, not just code, system design considerations and initial ideas and potential trajectories, what tools are right for the project come first priority at this stage.

### Notes
The next step is to define the satellite telemetry event design, including what fields each event should contain and what anomaly scenarios the system should be able to simulate and detect.

---

## Entry 002 - Telemetry Entities and Event Semantics (Sunday 5th April 2026)

### What I did
- Defined the core monitored telemetry entities in the satellite constellation system
- Decided that telemetry events should represent single timestamped observations (keeping things more simple)
- Decided on an initial set of event types: heartbeat, navigation, power, thermal, and comms
- Defined a small initial simulated satellite fleet and ground station set
- Identified the first broad anomaly categories the platform should eventually detect

### Why I did it
This establishes the conceptual model of the platform before writing any simulator code or cloud infrastructure. It ensures that telemetry generation, validation, detection, and analytics all in alignment and are semantically consistent.

### What I learned
A telemetry platform depends on consistent event semantics. If an event does not have a clear meaning, the downstream pipeline, rules, and analytics may become corrputed. Defining event intent early is the initial agreement on meaning and structure.

### Notes
The next step is to define the schema and the field level more precisely, including which fields belong to which event types and which fields should be mandatory or optional.

---

## Entry 003 - Telemetry Schema Design at The Field Level (Sunday 5th April 2026)

### What I did
- Elected to use a unified telemetry schema rather than separate schemas per event type
- Defined the common required metadata fields shared by all telemetry events
- Defined optional measurement fields that apply only to relevant event types
- Added conditional requirements for navigation, power, thermal, and comms events
- Defined initial allowed values for key categorical fields
- Established a validation philosophy covering presence, allowed values, numeric sanity, and rules that are aware of the event type

### Why I did it
This design gives the project a solid practical contract that is operationally realistic enough for a telemetry platform while still being simple enough to implement cleanly. It keeps ingestion and querying manageable without losing the event specific meaning.

### What I learned
A good telemetry schema balances semantic clarity with implementation practicality. Separate schemas may be more elegant as it means there would not be an abundance of nulls in event specific records, but a unified schema may often the better engineering choice when the goal is building a stable platform with simpler validation and analytics.

### Notes
The next step is to define the anomaly catalogue in some more detail, including what types of suspicious or faulty behaviour will be simulated and injected, and which fields each anomaly is expected to affect.

---

## Entry 004 - Anomaly Catalogue Design (Sunday 5th April 2026)

### What I did
- Defined the first simple anomaly catalogue for NYX
- Grouped anomalies into operational, navigation, communications, and security related categories
- Chose an initial anomaly set covering battery, thermal, signal, latency, packet integrity, position consistency, source trust, and replay  behaviour
- Assigned some initial severity levels to each anomaly
- Defined a hybrid detection philosophy combining deterministic rule based logic for abvious anomalies and future ML-based scoring for more subtle deviations and drift from the normal telemetry baseline

### Why I did it
The anomaly catalogue gives the project a realistic operational and security direction. It ensures that telemetry simulation is not random and that future validation, rules, and analytics are grounded in specific injected scenarios the platform is expected to detect.

### What I learned
Anomaly design is not just about inventing malformed or malicious data. It is about defining meaningful system failure and threat scenarios that affect specific telemetry fields in plausible ways that are mission sensitive for the context of a satellite constellation system. This makes the simulator, the detection layer, and the eventual dashboards far more coherent than they otherwise would be if it possessed more arbirary failure modes.

### Notes
The next step is to translate the schema design into a concrete structured contract, probably as a JSON Schema or a python schema validation model, so that the simulator and ingestion pipeline can enforce it consistently.

---