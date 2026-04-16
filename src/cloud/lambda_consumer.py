import base64
import json
import logging
import os

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import boto3

from pydantic import ValidationError
from simulator.contracts import TelemetryEvent, AuthStatus

# Deployment note:
# This module is intended to be packaged and deployed as the NYX bronze layer
# landing Lambda function once the AWS account and Terraform resources are ready.

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3_client = boto3.client("s3")
sns_client = boto3.client("sns")
cloudwatch_client = boto3.client("cloudwatch")

# Where each landed batch goes in the NYX bronze S3 bucket (example key: bronze/telemetry/ingestion_date=2026-04-11/satellite_id=NYX-SAT-001/batch_<uuid>.jsonl)
def build_s3_object_key(*, prefix: str, timestamp: datetime, batch_id: str) -> str:
    ingestion_date = timestamp.strftime("%Y-%m-%d")

    return (f"{prefix}/"f"ingestion_date={ingestion_date}/"f"batch_{batch_id}.jsonl")

# Decode base64 encoded Kinesis record and parse json
def decode_kinesis_record(record: dict[str, Any]) -> dict[str, Any] | None:
    try:
        encoded_data = record["kinesis"]["data"]
        decoded_data = base64.b64decode(encoded_data)
        decoded_str = decoded_data.decode("utf-8")
        return json.loads(decoded_str)

    except (KeyError, ValueError, json.JSONDecodeError) as exception:
        LOGGER.warning("Failure to decode Kinesis record: %s", exception)
        return None

# Writes quaratine record  
def build_quarantine_record(*, raw_record: dict[str, Any], ingestion_timestamp: str, error_message: str) -> dict[str, Any]:
    return {
        "ingestion_timestamp": ingestion_timestamp,
        "error_type": "validation_error",
        "error_message": error_message,
        "raw_record": raw_record
    }

# Writes a batch of JSON records as JSONL to S3, returns object key if records are written
def jsonl_batch_to_s3(
        *,
        bucket_name: str,
        prefix: str,
        records: list[dict[str, Any]],
        timestamp: datetime,
        batch_id: str
) -> str | None:
    if not records:
        return None
    
    s3_object_key = build_s3_object_key(
        prefix=prefix,
        timestamp=timestamp,
        batch_id=batch_id
    )

    jsonl_payload = "\n".join(json.dumps(record) for record in records) + "\n"

    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_object_key,
        Body=jsonl_payload.encode("utf-8"),
        ContentType="application/json"
    )

    return s3_object_key
        
# Determines if an SNS alert should be published for a validated (silver) event
def evaluate_sns_alert(event: TelemetryEvent) -> tuple[bool, str]:

    reasons: list[str] = []
    
    if event.auth_status == AuthStatus.FAILED:
        reasons.append("Authentication failure detected: potential security breach")
    
    if event.is_anomalous:
        reasons.append(f"Anomalous telemetry detected: {event.anomaly_type}")
    
    if event.battery_pct is not None and event.battery_pct < 30.0:
        reasons.append(f"Low battery levels detected: {event.battery_pct:.2f}% remaining")
    
    if event.temperature_c is not None and event.temperature_c > 70.0:
        reasons.append(f"Temperature levels exceeding operational threshold: {event.temperature_c:.2f} C")
    
    if event.temperature_c is not None and event.temperature_c < -20.0:
        reasons.append(f"Temperature levels below operational threshold: {event.temperature_c:.2f} C")
    
    if event.uplink_latency_ms is not None and event.uplink_latency_ms > 500.0:
        reasons.append(f"High uplink latency detected: {event.uplink_latency_ms:.2f} ms")
    
    if event.downlink_latency_ms is not None and event.downlink_latency_ms > 500.0:
        reasons.append(f"High downlink latency detected: {event.downlink_latency_ms:.2f} ms")
    
    if event.signal_strength_db is not None and event.signal_strength_db < -100.0:
        reasons.append(f"Weak signal strength detected: {event.signal_strength_db:.2f} dB")

    if event.packet_integrity_score is not None and event.packet_integrity_score < 0.95:
        reasons.append(f"Packet integrity degradation detected: score of {event.packet_integrity_score:.2f}")
    
    if event.auth_status == AuthStatus.FAILED or AuthStatus.UNKNOWN and event.anomaly_type is not None and event.packet_integrity_score is not None and event.packet_integrity_score < 0.95:
        reasons.append("Multiple indicators of potential critical security breach: authentication failure, anomalous telemetry, and packet integrity degradation")
    
    return (len(reasons) > 0, reasons)
    

# Build SNS alert message subhect and body for notification email
def build_alert_message(event: TelemetryEvent, reasons: list[str]) -> tuple[str, str]:

    subject = f"NYX Alert: {event.satellite_id} - {event.event_type.value}"

    reasons_msg = "\n".join(f"- {reason}" for reason in reasons)

    message = (
        f"NYX operational alert triggered\n\n"
        f"Reasons: \n{reasons_msg}\n\n"
        f"Satellite ID: {event.satellite_id}\n"
        f"Event ID: {event.event_id}\n"
        f"Event Type: {event.event_type.value}\n"
        f"Event Timestamp: {event.event_timestamp}\n"
        f"Anomaly Type: {event.anomaly_type}\n"
        f"Payload Status: {event.payload_status}\n"
        f"Status Code: {event.status_code}\n"
    )

    return subject, message


# Publish SNS alert
def publish_sns_alert(*, topic_arn: str, event: TelemetryEvent, reasoning: str) -> None:
    
    subject, message = build_alert_message(event, reasoning)

    sns_client.publish(
        TopicArn=topic_arn,
        Subject=subject,
        Message=message
    )

    LOGGER.info("Published SNS alert for event_id=%s, satellite_id=%s with reason: %s", 
                event.event_id, event.satellite_id, reasoning)


# Lambda entry point (writing to S3)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Consumes a Kinesis telemetry batch, then lands it into:
    - bronze/raw
    - silver/validated
    - quarantine/invalid
    - SNS alerts
    """
    bucket_name = os.environ["NYX_BRONZE_BUCKET"]
    bronze_prefix = os.environ.get("NYX_BRONZE_PREFIX", "bronze/telemetry")
    silver_prefix = os.environ.get("NYX_SILVER_PREFIX", "silver/telemetry")
    quarantine_prefix = os.environ.get("NYX_QUARANTINE_PREFIX", "quarantine/telemetry")

    alert_topic_arn = os.environ["NYX_ALERT_TOPIC_ARN"]

    records = event.get("Records", [])
    LOGGER.info("Received %s Kinesis records", len(records))

    decoded_records: list[dict[str, Any]] = []

    for record in records:
        decoded_record = decode_kinesis_record(record)
        if decoded_record is not None:
            decoded_records.append(decoded_record)

    if not decoded_records:
        LOGGER.warning("No valid records decoded from batch")
        return {
            "status": "no_valid_records",
            "received_records": len(records),
            "decoded_records": 0,
            "bronze_records": 0,
            "silver_records": 0,
            "quarantine_records": 0
        }
    

    timestamp = datetime.now(UTC)
    ingestion_timestamp = timestamp.isoformat()
    bronze_batch_id = str(uuid4())
    silver_batch_id = str(uuid4())
    quarantine_batch_id = str(uuid4())
    
    valid_records: list[dict[str, Any]] = []
    quarantine_records: list[dict[str, Any]] = []

    alerts_published = 0

    for raw_record in decoded_records:
        try:
            validated_event = TelemetryEvent(**raw_record) # Validation against original pydantic model contract

            alert_triggered, alert_reasoning = evaluate_sns_alert(validated_event)
            if alert_triggered:
                publish_sns_alert(
                    topic_arn=alert_topic_arn,
                    event=validated_event,
                    reasoning=alert_reasoning
                )

                alerts_published += 1

            validated_payload = validated_event.model_dump(mode="json")
            validated_payload["validated_at"] = ingestion_timestamp
            valid_records.append(validated_payload)
        
        except ValidationError as exception:
            quarantine_records.append(
                build_quarantine_record(
                    raw_record=raw_record,
                    error_message=str(exception),
                    ingestion_timestamp=ingestion_timestamp
                )
            )

    bronze_key = jsonl_batch_to_s3(
        bucket_name=bucket_name,
        prefix=bronze_prefix,
        records=decoded_records,
        timestamp=timestamp,
        batch_id=bronze_batch_id
    )

    silver_key = jsonl_batch_to_s3(
        bucket_name=bucket_name,
        prefix=silver_prefix,
        records=valid_records,
        timestamp=timestamp,
        batch_id=silver_batch_id
    )

    quarantine_key = jsonl_batch_to_s3(
        bucket_name=bucket_name,
        prefix=quarantine_prefix,
        records=quarantine_records,
        timestamp=timestamp,
        batch_id=quarantine_batch_id
    )


    LOGGER.info(
        (
            "Batch processed: received=%s decoded=%s bronze=%s silver=%s " 
            "quarantine=%s alerts_published=%s bronze_key=%s silver_key=%s quarantine_key=%s"
        ),
        len(records),
        len(decoded_records),
        len(decoded_records),
        len(valid_records),
        len(quarantine_records),
        alerts_published,
        bronze_key,
        silver_key,
        quarantine_key
    )

    publish_cloudwatch_metrics(
        namespace="NYX/Ingestion",
        received_records=len(records),
        decoded_records=len(decoded_records),
        silver_records=len(valid_records),
        quarantine_records=len(quarantine_records),
        alerts_published=alerts_published,
    )

    return {
        "status": "success",
        "received_records": len(records),
        "decoded_records": len(decoded_records),
        "bronze_records": len(decoded_records),
        "silver_records": len(valid_records),
        "quarantine_records": len(quarantine_records),
        "sns_alerts_published": alerts_published,
        "bronze_key": bronze_key,
        "silver_key": silver_key,
        "quarantine_key": quarantine_key,
    }


# Publish custom CloudWatch metrics
def publish_cloudwatch_metrics(
        *,
        namespace: str,
        received_records: int,
        decoded_records: int,
        silver_records: int,
        quarantine_records: int,
        alerts_published: int
) -> None:
    
    cloudwatch_client.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                "MetricName": "ReceivedEvents",
                "Value": received_records,
                "Unit": "Count"
            },
            {
                "MetricName": "DecodedEvents",
                "Value": decoded_records,
                "Unit": "Count"
            },
            {
                "MetricName": "SilverEvents",
                "Value": silver_records,
                "Unit": "Count"
            },
            {
                "MetricName": "QuarantineEvents",
                "Value": quarantine_records,
                "Unit": "Count"
            },
            {
                "MetricName": "AlertsPublished",
                "Value": alerts_published,
                "Unit": "Count"
            },
        ],
    )
    