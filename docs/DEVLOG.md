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

## Entry 016 - Telemetry Reader and JSONL Validation (Thursday 9th April 2026)

### What I did
- Added a validation summary model for JSONL telemetry file inspection
- Built a reader module that parses JSONL line by line and validates each record against the TelemetryEvent data contract
- Counted valid and invalid records, grouped valid events by event type, and grouped anomalous events by anomaly type
- Added a CLI validation script for inspecting generated telemetry files
- Added automated tests for valid files, mixed valid/invalid files, and files containing injected anomalies

### Why I did it
NYX needed to consume its own generated telemetry rather than only producing it. This validation step acts like an early data quality gate and makes the local output much more useful for debugging and later ingestion work before introducing any cloud infrastructure to the project.

### What I learned
A telemetry pipeline is stronger when the same data contract is used both at generation time and at validation time as a single source of truth. Reusing the contract reduces duplicated logic and helps ensure that the simulator and the reader agree concretely on what a valid event looks like.

### Notes
The next step is to build a lightweight analysis script on top of the validated telemetry so NYX can report simple operational findings, such as anomaly rate, battery distributions, or event type mix from a generated file.

---

## Entry 017 - Telemetry Analysis (Thursday 9th April 2026)

### What I did
- Implemented a telemetry analysis summary model for reporting simple metrics from validated JSONL files
- Built an analysis module that reads telemetry output, validates records, and computes event counts, anomaly counts, anomaly rate, and basic numeric summaries
- Added a CLI script to run the telemetry analysis from the command line
- Added automated tests for numeric summarization, file analysis, anomaly rate calculation, and invalid record handling

### Why I did it
Validation tells me whether the telemetry file is structurally correct (the data contract has been enforced), but analysis tells me what the file actually contains. This step starts turning simulator output into actual operational insight rather than just displaying the raw records.

### What I learned
Even a small analysis layer adds a lot of value when it is built on top of the same validation contract. It becomes much easier to reason about event mix, anomaly prevalence, and the basic shape of important metrics such as battery, temperature, and latency.

### Notes
The next step is to build a small run comparison workflow so NYX can compare two simulator outputs and show how anomaly rate or metric distributions differ between runs.

---

## Entry 018 - Telemetry Comparison (Friday 10th April 2026)

### What I did
- Added a comparison summary model for comparing two distinct analyzed telemetry runs
- Built comparison logic to evaluate changes in anomaly rate, event counts, anomaly counts, and selected metric averages
- Added a CLI script to compare two JSONL telemetry outputs directly from the command line
- Added automated tests for metric delta handling and comparison logic

### Why I did it
Singular analysis is useful, but operational work often depends on comparison and evolution over time. This step allows NYX to show how one simulator run differs from another, which is useful for anomaly-heavy versus anomaly-light runs and later for monitoring drift or changes in simulated system behaviour.

### What I learned
Comparison logic is easiest to build when each run already has a clean analysis summary. That separation keeps the design simple: first summarize each run, then compare the summaries rather than trying to compare raw files directly.

### Notes
The next step is likely just some housekeeping before I consider staging the project to use cloud infrastructure: documenting the simulator subsystem properly, reviewing the repository structure, and deciding whether to move next into local bronze/silver processing or detection and alerting logic.

---

## Entry 019 - Local Rule Based Alerting (Friday 10th April 2026)

### What I did
- Added a dedicated alert contract with alert types and severities
- Built a local rules engine that evaluates telemetry events for low battery, high temperature, weak signal, high latency, failed authentication, anomaly flags, and composite signals representing a more significant security breach (packet degradation, authentication failure, and anomaly flagged).
- Added alert generation from JSONL telemetry files
- Added alert summary output and optional alert JSONL
- Added automated tests for alert rule evaluation and file based alert generation

### Why I did it
This completes the local monitoring by allowing NYX not only to simulate telemetry and anomalies, but also to actively detect suspicious conditions and generate alert artifacts, so it doesnt just emit information but also evaluates itself. It makes the project act much more like an actual operational telemetry platform.

### What I learned
Telemetry and alerts are related but distinct layers. A telemetry event describes system state, while an alert represents a judgement that the state deserves attention. Separating those concepts makes the platform clearer and easier to extend in future as I may look into more nunances regarding satellite operational fields and further potential anomalies.

### Notes
This local rule based alerting pattern is a strong candidate for the future cloud based intentions for the project, where similar logic can be migrated into AWS services such as Lambda, S3, and SNS so it is easily transferable.

---

## Notes On The Cloud Engineering Aspects of NYX

Since the underlying observation, alerting, data contract enforcement, and telemetry structure are now completed locally in a manner that is easily scalable and extensible (I might augment the complexity of the telemetry platform), I have considered some approaches for cloud integration.

First, I have elected that NYX should have a streaming cloud ingestion architecture over a batch ingestion since this seems more in line with an actual satellite intelligence platform. So NYX will have streaming AWS ingestion, laking the local simulator telemetry and ingesting to to a AWS native raw landing zone. 

The cloud shape I am considering is the following:

- Kinesis data stream
- Lambda consumer
- S3 bronze raw landing
- CloudWatch logs

The current simulator emits structured telemetry events one at a time in sequence, which comfortable allows me to construct a producer for a data stream.

I decided that Kinesis is a good ingestion buffer as it provides: streaming semantics, durability for incoming records, decoupling between the stream producer and consumer, and has a proper AWS telemetry ingestion.

Lambda allows for serverless processing, a direct connection from Kinesis, a low operational overhead, and some room for validation and enrichment later on.

S3 bronze storage is durable, allows for replayability, serves as a good future analytics path, and also serves the foundation for a medallion lakehouse architecture (bronze/silver/gold).

Cloudwatch would provide visibility, debugging, and error tracing.

This initial cloud architecture is what I will be implementing as a baseline. After I have confidently verified that NYX can stream telemetry into AWS and land the raw records cleanly into an S3 bronze layer, I can consider adding other services such as grafana, Athena, Glue, and such. 

### The Streaming Ingestion Foundation

The objective is to get live telemetry events from the local NYX telemetry simulator into AWS and land this data into an S3 storage bronze layer through a serverless comsumer.

Initially I want to establish the following:
- Kinesis stream
- An S3 bucket
- Lambda consumer
- IAM roles and policies
- CloudWatch logs
- Infrastructure as code (terraform)
- A local producer script that sends simulator events to Kinesis as JSON

Later I can add the following:
- Silver transformations
- Athena SQL queries
- Alerting within the cloud
- Data quarantine policy
- Dashboards
- SNS notifications

### Data FLow Overview

1) Local NYX simulator emits a JSON telemetry event
2) The telemetry output is sent to Kinesis as JSON via a producer script
3) Kinesis buffers the event
4) Lambda consumer is triggered by the Kinesis records
5) Lambda proceeds to write raw event JSON into S3 under a bronze prefix
6) Lambda logs write success/failure details to CloudWatch

### S3 Bronze Layout

The following layout is considered: 

```bash
s3://NYX/
  bronze/
    telemetry/
      ingestion_date=YYYY-MM-DD/
        satellite_id=NYX-SAT-001/
          <events>.jsonl
```

This S3 bucket architecture clearly marks raw landed telemetry with `bronze/telemetry/`, and the ingestion date provides date partitioning (partitioning is a good practice for efficient database searches), and the satellite id provides further partitioning which is useful for organisation. 

This layout supports the later planned Athena / Glue work.

I could do temporal partitioning such as partitions by hour, but I will keep it simple for now.

### Object Writing

I have decided to have lambda batch multiple Kinesis records into a single S3 object.

So, the lambda consumer receives a batch from Kinesis, decodes the records from the batch, then writes them as a JSONL payload to a single S3 object.

Each Lambda invocation produces one law landing object containing multiple events.


### Kinesis Design

I am starting with 1 shard, this should be enough to show producer / consumer integration and the intended streaming design without excessive project scope.

The record payload is a UTF-8 JSON string, and one elemetry event partitioned by the key `satellite_id`.

### Lambda Consumer Responsibilities

Initially Lambda needs only to do the following:

- Decode Kinesis records
- parse payloads as JSON
- potentially could do minimal validation
- write batches to S3 as JSONL
- log metadata to CloudWatch

If this all works as intended then I will move on to anomaly detection, alert generation, quarantine routines, metric aggregation, and data enrichment

### Initial Validation Approach

Initially I want to only do minimal validation only for the following:

- JSON decode must be successful
- confirm core keys exist: event_id, event_timestamp, satellite_id, event_type
- Invalid records are logged in CloudWatch and skipped for now (quarantine paths come later)


### IAM Policies and Basic Security

For some basic security I will consider the following:

- S3 bucket has blocked public access, enabled encryption at rest, maybe versioning
- Lambda execution should allow writes to S3 bucket bronze prefix, writes to CloudWatch logs, and reads from the Kinesis stream event source mapping context

I will need to think about the producer credentials.

The best approach for this initial stage could involve unsing a local AWS CLI profile / IAM user credentials. The producer script can use the boto3 library locally.

### Initial Observability Principles

Keeping this light for now. The CloudWatch logs from Lambda may include batch size, the number of records written to S3 successfully, the target S3 object key, the skipped/failed record write count. Later one I can implement custom metrics, alarms and dashboards.

### Artifact flow

Because I am extending NYX to cloud, it essentially has two output modes: local artifacts, and the streaming cloud path.

The local artifacts or the telemetry JSONL files, the run summaries, the alerts JSONL, and the alert summaries.

For the streaming cloud path, initially I will only stream the raw telemetry events to AWS in near real time. I am not going to stream the summaries and alerts to AWS because when the cloud alerting is implemented, the cloud alerts become their own artifact stream, there would be little point having two streams of artifacts effectively saying the same thing.

---

## Entry 020 - Streaming Cloud Ingestion Design (Friday 10th April 2026)

### What I did
- Defined the first cloud architecture for NYX as a streaming ingestion path
- Chose Kinesis Data Streams as the ingestion layer and Lambda as the serverless consumer
- Defined S3 bronze landing as the first raw cloud storage target
- Chose a batch to object Lambda write pattern to avoid inefficient one object per event behaviour
- Scoped the first cloud implementation strategy to streaming ingestion, raw landing, logging, and infrastructure provisioning and nothing more as a baseline

### Why I did it
NYX is fundamentally a telemetry and monitoring platform, so a streaming ingestion path is a better fit than a purely batch cloud design. This architecture preserves the real time streaming essence of the simulator while still staying manageable for the scope of this project.

### What I learned
A good streaming architecture does not need to include every AWS service at once, this would be overhelming and overcomplicating the deliverable. Kinesis, Lambda, S3, and CloudWatch are enough to establish an effective near real time streaming ingestion foundation without overcomplicating the system.

### Notes
The next step is to create the Terraform skeleton for the cloud resources and begin provisioning the first streaming ingestion components.

---

## Entry 021 - Cloud Infrastructure Skeleton and Initial Terraform Setup (Friday 10th April 2026)

### What I did
- Created the initial cloud centric repository structure for NYX
- Added a dedicated Terraform directory under infra/terraform
- Added initial Terraform files for provider configuration, variables, outputs, and example variable values
- Added placeholder Python modules for the future Kinesis producer and Lambda consumer
- Initialized Terraform locally to confirm the infrastructure scaffold is ready for resource implementation

### Why I did it
Before provisioning any AWS resources, I wanted a clean and intentional infrastructure layout as a foundational scaffold to build from. This makes the cloud implementation easier to build, explain, and maintain without mixing infrastructure code into the simulator logic which can end up messy.

### What I learned
A good infrastructure project benefits from the same discipline as applied in application code: structure first, followed by resources. Even a small Terraform scaffold makes the cloud work feel more deliberate and allows me to more easily see what to extend and why.

### Notes
The next step is to add the first real AWS resources, the S3 bronze landing bucket and the Kinesis telemetry stream.

---

## Entry 022 - Initial AWS Resources: S3 Bronze Bucket and Kinesis Stream (Friday 10th April 2026)

### What I did
- Added the first real AWS resources to the NYX Terraform configuration
- Created a secure S3 bronze bucket with versioning, server-side encryption, and public access blocking
- Created a Kinesis Data Stream for NYX telemetry ingestion
- Updated Terraform outputs to reference live resource attributes rather than only configuration variables
- Ran Terraform formatting, validation, and planning to confirm the initial cloud resources are valid and ready to provision

### Why I did it
This step establishes the first real cloud foundation for NYX. The S3 bucket provides durable raw storage for landed telemetry, while Kinesis provides the streaming ingestion layer that matches the telemetry-driven nature of the project.

### What I learned
Even a small AWS footprint benefits from baseline security controls. S3 encryption, blocked public access, and clear tagging are simple additions that materially improve the credibility of the infrastructure.

### Authentication Issue
Terraform configuration validated successfully, but the first plan failed because no AWS credential source was configured locally.

### Resolution
I created a new IAM user specifically for this project, granted it programmatic access and full S3 access and Kinesis full access initially under an admin group I constructed, this will be reconfigured down the line for more secure permissions and role allocations in future.

I then Configured local AWS credentials via AWS CLI and verified access using `aws sts get-caller-identity` before rerunning Terraform plan.

### Security refinement
Before applying the first cloud resources, I enabled server-side encryption for the Kinesis stream using the AWS-managed Kinesis KMS key. This brought the ingestion layer more in line with the security already applied to the S3 bronze bucket, both now have encryption.

### Learning
Valid Terraform syntax is not enough for cloud provisioning. The provider also needs authenticated access to the target AWS account in order to build a real execution plan.

Baseline security controls should be applied early when they are cheap to add. Although, leaving the stream unencrypted would have worked technically, but it would have been a weaker engineering choice for a telemetry and defence/intelligence centered platform.

### Notes
The next step is to add the Lambda consumer infrastructure, including the execution role and the event source mapping from Kinesis to Lambda.

---

## Entry 023 - Lambda Bronze Landing Consumer (Local Build First) (Saturday 11th April 2026)

### What I did
- Implemented the first version of the NYX Lambda consumer for bronze landing
- Added logic to decode Kinesis records from base64, parse JSON payloads, and batch valid records into a JSONL object
- Added S3 object key generation for bronze telemetry landing using ingestion date and satellite ID
- Added a mock Kinesis event fixture for local testing
- Added automated tests for Kinesis record decoding and S3 key generation

### Why I did it
The AWS account was not yet ready for full deployment work due to a account verification issue which impacted my ability to establish any Kinesis infrastructure at this point, so I decided that the Lambda consumer logic could still be developed locally.

### What I learned
It is beneficial to maintain momentum in cloud projects is to separate service deployment from application logic. Even before any deployment, the Lambda function can be designed, tested, and documented locally using realistic event fixtures.

### Notes
The next step is to wire this consumer into Terraform by adding the Lambda execution role, Lambda resource, and Kinesis event source mapping once the account is ready.

---

## Entry 024 - Lambda Deployment and Kinesis Event Source Mapping (Saturday 11th April 2026)

### What I did
- Added a packaging script for the NYX Lambda consumer including both cloud and simulator scripts so dependencies are accounted for
- Added the Lambda execution role and inline IAM policy for CloudWatch logging, S3 writes, and Kinesis reads
- Added relevant Lambda and IAM permissions to the nyx admin group containing the primary admin user I am using to allow terraform apply to finalize
- Added the Lambda function resource to Terraform using the packaged deployment artifact
- Added environment variables for bronze landing configuration
- Added the Kinesis event source mapping so the Lambda can consume telemetry batches automatically

### Why I did it
This step turns the cloud architecture from separate resources into a connected ingestion pipeline. With the event source mapping in place, NYX now has the essential serverless path needed to receive telemetry events from the stream and land them into S3.

### What I learned
Connecting serverless components requires both infrastructure and workload packaging. The IAM role, Lambda packaging path, and event source mapping are all necessary pieces of the same pipeline, and missing any one of them breaks the flow.

### Notes
The next step is to build the local Kinesis producer and test the first complete streaming flow from simulator to Kinesis to Lambda to S3.

---

## Entry 025 - First Full Cloud Telemetry Flow (Saturday 11th April 2026)

### What I did
- Built a local Kinesis producer that sends NYX telemetry events into the telemetry stream
- Reused the existing event factory cycle so cloud ingestion uses the same event shapes and logic as the local simulator
- Sent a controlled batch of telemetry events into AWS
- Verified Lambda invocation and CloudWatch logs for the bronze landing consumer
- Verified that raw telemetry batches were landed into the S3 bronze layer as JSONL objects

### Why I did it
This was the first true cloud test for NYX. It connected the local telemetry generator to the cloud ingestion pipeline and proved that the system can move events from producer to stream to serverless consumer to durable raw S3 storage.

### What I learned
A cloud pipeline is only really authentic once data actually moves through it. Deliberately witnessing the telemetry travel from a local producer into AWS and land successfully in S3 made the architecture much more concrete and exposed the importance of log inspection and verification.

### Issue with S3 architecture semantics

Although the pipeline works successfully, there is an issue with semantics in the S3 bronze layer. Lambda receives a batch of Kinesis records, decodes them, and looks at the first records satellite_id value, which means the entire batch is written to: `bronze/telemetry/ingestion_date=.../satellite_id=<first satellite>/batch_<uuid>.jsonl`. So if the batch contains the other satellite_id, this naming is misleading as the assumption is this is a bronze partition for exclusively the one satellite id, but the actual records contained all 3 satellite_id in events.

Specifically, the first record for my pipeline test, streaming 10 events had the first record being `satellite_id=NYX-SAT-002`, and so the whole file lands under that satellite_id.

This is a design bug, the data is fine but the folder is misleading. I want to solve this before dealing with Athena partitions, and I could handle partitions in a silver transformation layer and just have bronze partition by ingestion data or possible hour as well.

### Notes

First I will fix the bronze S3 key structure, removing satellite_id from the S3 path, keeping ingestion data as the partition, keeping the batched JSONL files and redeploy Lambda.

Then the next step is to improve the cloud ingestion path with stronger validation and possibly a quarantine path for malformed records, or to begin adding query and analytics capability over the landed bronze data.

---
---

## Entry 026 - Bronze Layer Partition Fix (Tuesday 14th April 2026)

### What I did
- I removed the satellite_id centered bronze partitioning from the bronze S3 object key in the lambda consumer code
- Updated the lambda consumer to land telemetry batches using ingestion_date exclusively (not further partitioning)
- Redeployed the Lambda function to AWS and verified new S3 object structure. Now the partitions make sense and are not misleading

### Why I did it
The previous design incorrectly implied that each landed batch contained data for a single satellite, which is not guaranteed when consuming batched records from Kinesis. This created a mismatch between storage layout and actual data.

### What I learned
Bronze data layers should remain as close to raw ingestion reality as possible. Partitioning based on payload fields should only be done when the ingestion process guarantees that structure, or later in downstream transformation layers.

### Notes
Future silver transformations can repartition data by satellite_id or other fields once records are validated and reorganized.

---

## Entry 027 - Cloud Validation, Silver Landing, and Quarantine Routing (Tuesday 14th April 2026)

### What I did
- Upgraded the NYX Lambda consumer to validate decoded telemetry records using the shared TelemetryEvent contract
- Added routing logic so decoded records are written to bronze as raw ingestion data, valid records are written to silver, and invalid records are wrapped with error metadata and written to quarantine
- Added a validated_at field to silver records for lineage
- Updated Terraform environment variables so the Lambda knows the bronze, silver, and quarantine prefixes
- Redeployed the Lambda and prepared the pipeline for full end to end validation testing

### Why I did it
A telemetry ingestion pipeline should not assume every decoded record as equally trustworthy. This step adds a real cloud-side trust boundary by separating raw landed data from validated telemetry and malformed records.

### What I learned
Bronze, silver, and quarantine each serve different purposes within the medallion data architecture. Bronze preserves ingestion reality, silver represents validated trustworthy data, and quarantine captures records that need investigation without polluting trusted downstream layers with sufficient metadata for tracibility.

### Notes
The next step is to run a test that includes an intentionally invalid record so the quarantine path can be verified alongside normal bronze and silver routing.

### Packaging issue encountered
After adding validation on the cloud end with the shared Pydantic telemetry contract, Lambda invocations no longer produced S3 outputs. The issue was that the deployment zip only contained project source code and did not include the Pydantic dependency required at runtime.

### Resolution
Updated the Lambda packaging script to bundle Linux-compatible Pydantic dependencies into the deployment artifact before redeploying the function.

### Learning
Lambda deployment packages must include all dependencies in a format compatible with the Lambda execution environment. Local tests passing is not sufficient if the deployed artifact is missing required libraries it will not run on in the cloud environment.

---

## Entry 028 - Quarantine Path Verification (Tuesday 14th April 2026)

### What I did
- Created a dedicated invalid telemetry event sender
- Injected a deliberately invalid record into the Kinesis stream (battery_pct > 100)
- Verified that the Lambda consumer routed the record correctly in AWS S3 console

### Results
- Bronze layer received the raw invalid record
- Silver layer correctly excluded the invalid record
- Quarantine layer stored the invalid record with validation error metadata
- CloudWatch logs showed correct routing counts (bronze=1, silver=0, quarantine=1)

### What I learned
A robust data pipeline should explicitly handle invalid data, not just process valid data while not enforcing the underlying data contract. The quarantine layer provides traceability and debugging capability without polluting trusted datasets.

### Notes
This confirms that the NYX ingestion pipeline enforces data contracts in the cloud and maintains a clear separation between raw, validated, and invalid telemetry data

---

## Entry 029 - Athena and Glue Query Layer Design (Tuesday 14th April 2026)

### What I did
- Designed the first cloud query layer for NYX using Athena and the Glue Data Catalog AWS services
- Chose the validated silver telemetry prefix as the first queryable dataset 
- Defined the initial Athena schema for silver telemetry JSON records
- Chose ingestion_date as the first partition key
- Identified a few of the first useful operational SQL queries for event mix, anomaly counts, battery health, latency, and thermal extremes

### Why I did it
NYX now has a functioning ingestion and validation pipeline, so naturally next logical step is to make trusted telemetry queryable in the cloud. Athena and Glue services provide a lightweight AWS analytics layer.

### What I learned
A cloud query layer works best when it is built on top of a trusted and validated dataset. Querying silver rather than bronze keeps the analytics path clean and reinforces the value of the validation and quarantine boundary.

### Notes
The next step is to provision the Athena results bucket (seperate bucket from the bronze / silver / quarantine) and Glue database, then register the first silver telemetry table.

Later I could consider writing data to parquet since this is more computationally and cost efficient, but I will focus on setting the foundation first with the data already in S3 storage. I could also consider further data partitions for better query performance.

---

## Entry 031 - Glue Table Registration for Silver Telemetry (Wednesday 15th April 2026)

### What I did
- Added a Glue catalog table for the NYX silver telemetry dataset
- Mapped the validated telemetry schema into an explicit Athena SQL queryable external table definition
- Partitioned the table by ingestion_date to match the silver S3 prefix layout
- Applied the metadata definition through Terraform and verified the table in AWS Glue
- Prepared the query layer for Athena by planning partition repair and first SQL checks

### Why I did it
Landing validated telemetry in S3 is the foundation, the project needed a cloud analytics layer to become a proper data platform. Registering silver telemetry in Glue makes the validated data queryable with Athena.

### What I learned
Cloud queryability depends on metadata as just as much as the actual data. Even when valid files already exist in S3, Athena needs an explicit schema and partition awareness before SQL can become useful.

### Notes
The next step is to repair partitions in Athena and run the first operational queries against the silver telemetry layer.

---

## Entry 032 - SNS Alerting Infrastructure (Wednesday 15th April 2026)

### What I did
- Added an SNS topic for NYX operational alerts
- Added an email subscription for alert delivery
- Updated Terraform outputs to expose the SNS topic name and ARN
- Applied the new alerting infrastructure and confirmed the email subscription

### Why I did it
The platform needed a real time response mechanism, not just data storage and queryability. SNS provides a simple AWS alerting channel that can later be triggered by the ingestion Lambda when suspicious telemetry is detected as defined by a set of alerting rules.

### What I learned
Alerting infrastructure is only partially configured until the notification endpoint is confirmed. Even when Terraform succeeds, the human subscription confirmation step is still required before messages can actually be delivered.

### Notes
The next step is to update the Lambda consumer so records are published to the SNS topic during ingestion and alerts are sent to email.

---

## Entry 033 - Cloud SNS Alert Publishing (Wednesday 15th April 2026)

### What I did
- Added SNS publish permission to the Lambda execution role
- Added the SNS topic ARN as a Lambda environment variable
- Extended the Lambda consumer to evaluate valid telemetry for alerting conditions
- Added SNS message construction and publishing for all anomalous alert scenarios currently accounted for in the alerting engine script
- Added automated tests for alert evaluation and message construction

### Why I did it
NYX needed to progress from storing and querying telemetry to reacting to important events in near real time. SNS provides a simple response path that makes the system feel more operational rather than just a purely analytical data platform.

### What I learned
An alerting channel becomes useful only when it is connected to clear rules and meaningful message content. Publishing an SNS message is technically simple, but building a useful alert requires enough context for a human to act on it effectively and with urgency.

### Notes
The next step is to verify the alert flow with a known alert populated telemetry event and confirm delivery through email and CloudWatch logs.

---

## Entry 034 - SNS Alert Flow Verification (Wednesday 15th April 2026)

### What I did
- Created a alert triggering telemetry sender for SNS verification
- Sent a communications event with failed authentication, high latency, degraded payload status, and anomaly metadata into the Kinesis stream
- Verified that the event passed contract validation and landed in bronze and silver
- Verified that the Lambda consumer published an SNS alert
- Confirmed alert delivery through email

### Why I did it
This was the definitive proof that NYX can react to critical telemetry conditions in near real time. It confirmed that alerting events can move from ingestion through validation and storage into an operational notification path.

### What I learned
A good alert test should use a data contract valid event that is operationally suspicious, rather than an invalid event that just gets quarantined. This preserves the distinction between bad data and valid but dangerous telemetry.

### Notes
The next steps can focus on reducing alert noise, adding severity logic, improving observability, or building cloud dashboards and analytics views.

### Alert duplication issue
Multiple SNS alerts were being emitted for a single event because each alert condition triggered independently.

### Resolution
Refactored alert evaluation to aggregate multiple conditions into a single alert with a list of reasons.

### Learning
One well-structured alert is more useful than multiple fragmented alerts for the same event.

---


