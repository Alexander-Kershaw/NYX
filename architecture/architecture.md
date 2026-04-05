***

# NYX - System Architecture

***

## Initial System Intentions

**NYX** is intended to to simulate mission sensitive telemetry from a small satellite constellation and process that information through a secure AWS-native pipeline.

## Planned Flow

- Satellite Telemetry Simulator
- Real-time telemetry stream ingestion
- Validation and quarantine layer against data contractts
- Bronze abstract storage
- Silver transformation and enrichment
- Detection layer (rules and ML implementation)
- Gold analytics and monitoring / alerting
- Query and dashboard layer

---