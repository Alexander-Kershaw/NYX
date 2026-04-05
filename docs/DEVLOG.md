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