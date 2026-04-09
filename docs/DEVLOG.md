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

## Entry 005 - Initial Pydantic Telemetry Contract (Monday 6th April 2026)

### What I did
- Set up the initial Python contract for telemetry events using Pydantic
- Defined enums for controlled categorical fields such as event type, authentication status, payload status, mission mode, and orbit class, meaning they stay consistent and support data integrity
- Created the first TelemetryEvent model with required metadata fields and the optional measurement/context fields
- Added some initial validation rules for battery percentage, packet integrity, latitude, and longitude
- Created a small sample script to instantiate and print a valid telemetry event

### Why I did it
This step turns the earlier schema design into actual executable validation logic. It creates a concrete data contract that can be reused by the simulator, tests, and the later ingestion components.

### What I learned
A schema design becomes much more useful when it is encoded as a programmatic contract. Pydantic acts as a gatekeeper by enforcing allowed structures and values before bad data can spread into the rest of the system.

### Notes
The next step is to improve the contract by adding event type awareness to the validation logic, so that fields like latitude and velocity are required for navigation events, while communications events require fields like latency and packet integrity.

---

## Entry 006 - Event Type Aware Validation (Monday 6th April 2026)

### What I did
- Added a model validation to the TelemetryEvent contract
- Enforced conditional required fields based on specific event types
- Required navigation events to include position and velocity fields
- Required power, thermal, and comms events to include the relevant subsystem fields
- Added a valid and invalid sample telemetry example to confirm the validation behaviour is working as intended

### Why I did it
A telemetry contract should not only validate individual field ranges, but should also enforce that the event makes contextual sense as a whole. Event type aware validation makes the schema significantly stronger by checking that each distinct kind of event includes the fields it logically requires.

### What I learned
There is a key difference between field validity and semantic validity. A field can be valid in isolation but still be wrong in another context. Validation at the TelemetryEvent model level helps enforce meaning of the fields, not just shape.

### Notes
The next step is to add proper automated tests for the contract so that valid and invalid event behaviour can be checked repeatedly as the project grows.

### Issue encountered
Initially I used `@field_validator(mode="after")` for event type validation, which caused a TypeError because field validators require a specific field name, but the fields are associated with a universal TelemetryEvent model schema, so I couldn't validate them in isolation.

### Resolution
Replaced with `@model_validator(mode="after")`, which is designed for validating relationships across multiple fields rather than just singular field validation rules.

### Learning
Field validators operate on individual fields, while model validators operate on the entire object. So, event type aware validation requires model-level validation.

### Additional issue encountered
Using `use_enum_values=True` caused enum fields such as `event_type` to behave like plain strings inside the model, which broke conditional validation logic that based on enum comparisons.

### Resolution
Removed `use_enum_values=True` from the model configuration and used `model_dump(mode="json")` when serializing output instead so the use of enum comparison logic is not broken.

### Learning
It is better to keep enums as typed values inside the model for internal validation and logic, then convert them to JSON only when exporting or printing data to avoid encountering this issue again.

---

## Entry 007 - Automated Contract Tests with Pytest (Monday 6th April 2026)

### What I did
- Added pytest automated tests for the telemetry contract
- Wrote passing tests for valid navigation and communications events
- Wrote failing tests for missing required navigation fields and invalid numeric ranges

### Why I did it
Manual checks are useful early on, but automated tests are necessary to keep the contract trustworthy as the project evolves over time. These tests provide a repeatable way to confirm that valid telemetry is accepted and invalid telemetry is rejected in a consistent manner.

### What I learned
A validation contract becomes significantly more valuable once it is backed by automated tests. Tests serve as regression tripwires, warning me when later changes break assumptions that were previously held which could indicate some broken logic or malformation in the schema contract.

### Notes
The next step is to clean up the package structure slightly and begin building the telemetry simulator itself, using the contract to generate valid mission-style events.

---

## Entry 009 - Multiple Type Telemetry Event Factories (Monday 6th April 2026)

### What I did
- Extended the simulator factory layer to generate the other event types: heartbeat, power, thermal, and comms events in addition to navigation
- Added a small internal helper to standardize how identifiers are selected to avoid repeating logic for each of the event type builder functions
- Updated the event generation script to emit a mixed set of telemetry events covering all the event types
- Expanded pytest coverage to validate that each event factory telemetry builder function returns the correct event type and required fields

### Why I did it
A realistic telemetry platform would need more than one kind of event so it is faithful to the complexities and multfactoral nature of space instrumentation operations. Adding multiple event factories makes the eventual simulator capable of producing a richer and more believable operational stream while still staying aligned with the contract as it is built from the contract.

### What I learned
Separating event generation by telemetry type keeps the code more readable and easier to extend in future if I wish to do so. It also reflects a foundational engineering pattern, shared scaffolding with specialised builders for different output shapes, allowing for an extendable and intuative telemetry generation architecture.

### Notes
The next step is to build a simple simulator loop that emits a sequence of mixed telemetry events over time rather than just singular samples to emulate a satellite telemetry stream encompassing an array of operational subsystems.

---

## Entry 010 - First Simulator Loop (Tuesday 7th April 2026)

### What I did
- Built the first NYX simulator loop to emit a repeating stream of mixed and distinct telemetry events
- Added an ordered cycle of event factories covering the event types: heartbeat, navigation, power, thermal, and comms
- Added basic command line arguments to control the number of emitted events and the delay between events
- Added a test to verify that the simulator factory cycle contains the expected event types in the expected order

### Why I did it
The project needed to move from singular event generation to a controlled telemetry stream. The simulator loop provides the first version of continuous event emission while still staying simple and easy to reason about.

### What I learned
A simulator is more than just an arbitrary random event generator. It needs an orchestration layer that controls cadence and event mix. Starting with a deterministic cycle makes the system easier to debug before introducing more realism with satellite specific awareness or randomness, and eventual anomalous telemetry injections.

### Notes
The next step is to improve realism by introducing per-satellite state, so repeated events from the same satellite evolve more coherently over time instead of being generated as isolated snapshots.

---

## Entry 011 - Per-Satellite State and Stateful Simulator (Tuesday 7th April 2026)

### What I did
- Added a SatelliteState model to represent the instantaneous internal state of each simulated satellite
- Built a state manager to initialize the fleet and evolve navigation, power, thermal, and comms metrics over time
- Added satellite state aware event builders that create telemetry directly from current satellite state so events make more sense in sequence
- Built a stateful simulator loop that updates satellite state before emitting relevant event types
- Added automated tests for state initialization, state evolution, and stateful event generation

### Why I did it
The earlier simulator emitted valid events, but each event was largely independent. Introducing a per-satellite state makes the telemetry stream more realistic by giving each satellite continuity over time rather than just a collection of independent snapshots of telemetry in time.

### What I learned
A simulator becomes much more believable when it remembers its previous conditions. Stateful simulation creates temporal coherence, which is important for anomaly detection, authentic operational analytics, and realistic debugging down the line.

### Notes
The next step is to add controlled anomaly injection so the stateful simulator can produce both nominal and suspicious telemetry patterns so monitoring has an actual purpose later in the project.

---

## Entry 012 - Controlled Anomaly Injection (Thursday 9th April 2026)

### What I did
- Added an anomaly module with named anomaly types for battery drain, thermal runaway, signal degradation, and spoofed source behaviour
- Implemented controlled anomaly injection functions that mutate satellite state or affect event context according to the anomaly being injected
- Updated the stateful event builders so emitted telemetry can carry anomaly metadata and degraded status markers
- Created a test script to show nominal and anomalous telemetry side by side verifying injection works
- Added automated tests covering state mutation and anomaly aware event generation

### Why I did it
The project needed a deliberate way to simulate incidents rather than relying only on healthy telemetry. Controlled anomaly injection makes the simulator useful for testing future validation, alerting, and anomaly detection logic.

### What I learned
Anomalies are more useful when they are named, bounded, and intentionally applied to nominal satellite states. Separating normal state evolution from anomaly injection makes the simulator easier to reason about and makes future detection logic more defensible.

### Notes
The next step is to integrate anomaly injection into the simulator loop with a configurable anomaly rate so NYX can emit both normal and anomalous telemetry during a single run.

---

## Entry 013 - Anomaly Stateful Simulator Loop (Thursday 9th April 2026)

### What I did
- Added helper functions to map anomaly types to supported event types
- Added probability based anomaly selection using a configurable anomaly rate
- Updated the stateful simulator loop to optionally inject anomalies during live event emission
- Added a command line parameter to control anomaly frequency during simulator runs
- Added automated tests for anomaly selection behaviour

### Why I did it
The simulator needed to move beyond just isolated anomaly emissions and start producing mixed operational streams containing both healthy and anomalous telemetry. This makes the project much more useful for the planned downstream validation, alerting, and analytics work.

### What I learned
Anomaly injection becomes much more manageable when it is constrained by event type and driven by explicit probability. This avoids unrealistic combinations and keeps the simulator output interpretable.

### Notes
The next step is to persist simulator output to a file, so NYX can generate structured telemetry datasets for later validation, analysis, and cloud ingestion.

---

## Entry 014 - Persisting Telemetry to JSONL Files (Thursday 9th April 2026)

### What I did
- Added IO helper functions for creating output directories and timestamped JSONL file paths
- Updated the stateful simulator so it can optionally write emitted telemetry to disk while still printing events to the terminal
- Configured the simulator to write one JSON event per line in a JSONL output file
- Added automated tests for the output directory and file path helper functions

### Why I did it
The simulator needed to move beyond terminal only output and start producing reusable telemetry artifacts. Writing JSONL files creates a local bronze layer dataset that can later feed validation, analytics, and cloud ingestion steps.

### What I learned
JSONL is a strong fit for event oriented data because it is append friendly, easy to inspect, and more simple to parse. Separating output path logic into a helper module keeps file management clean and avoids cluttering the simulator loop.

### Notes
The next step is to add summary statistics or run metadata so each simulator execution produces not just raw telemetry but also a small operational summary of what happened during the run.

---

## Entry 015 - Run Metadata and Summary Statistics (Thursday 9th April 2026)

### What I did
- Added a structured run summary model for telemetry simulator executions
- Updated the stateful simulator to track event counts and anomaly counts during a run for summaries
- Added grouped counts for emitted event types and anomaly types
- Configured the simulator to print a run summary at the end of execution
- Added optional JSON summary file output alongside the JSONL telemetry output
- Added automated tests for summary path generation and summary model behaviour

### Why I did it
Raw telemetry output is useful, but each simulator run should also leave behind a concise operational summary. This makes the simulator easier to inspect, debug, document, and validate.

### What I learned
A run summary in the context of satellite telemetry is potentially reminicent of a mission sensitive operational report. It gives immediate visibility into what happened during a satellite simulation run without needing to manually scan the entire telemetry output file.

### Notes
The next step is to begin building a lightweight validation and analysis layer over the generated telemetry, starting with reading JSONL output back in and checking quality metrics.

---


