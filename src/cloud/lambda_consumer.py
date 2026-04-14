import base64
import json
import logging
import os

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import boto3

from pydantic import ValidationError
from simulator.contracts import TelemetryEvent

# Deployment note:
# This module is intended to be packaged and deployed as the NYX bronze layer
# landing Lambda function once the AWS account and Terraform resources are ready.

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3_client = boto3.client("s3")

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
        

# Lambda entry point (writing to S3)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Consumes a Kinesis telemetry batch, then lands it into:
    - bronze/raw
    - silver/validated
    - quarantine/invalid
    """
    bucket_name = os.environ["NYX_BRONZE_BUCKET"]
    bronze_prefix = os.environ.get("NYX_BRONZE_PREFIX", "bronze/telemetry")
    silver_prefix = os.environ.get("NYX_SILVER_PREFIX", "silver/telemetry")
    quarantine_prefix = os.environ.get("NYX_QUARANTINE_PREFIX", "quarantine/telemetry")

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

    for raw_record in decoded_records:
        try:
            validated_event = TelemetryEvent(**raw_record) # Validation against original pydantic model contract
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
            "quarantine=%s bronze_key=%s silver_key=%s quarantine_key=%s"
        ),
        len(records),
        len(decoded_records),
        len(decoded_records),
        len(valid_records),
        len(quarantine_records),
        bronze_key,
        silver_key,
        quarantine_key,
    )

    return {
        "status": "success",
        "received_records": len(records),
        "decoded_records": len(decoded_records),
        "bronze_records": len(decoded_records),
        "silver_records": len(valid_records),
        "quarantine_records": len(quarantine_records),
        "bronze_key": bronze_key,
        "silver_key": silver_key,
        "quarantine_key": quarantine_key,
    }