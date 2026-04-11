import base64
import json
import logging
import os

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import boto3

# Deployment note:
# This module is intended to be packaged and deployed as the NYX bronze layer
# landing Lambda function once the AWS account and Terraform resources are ready.

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3_client = boto3.client("s3")

# Where each landed batch goes in the NYX bronze S3 bucket (example key: bronze/telemetry/ingestion_date=2026-04-11/satellite_id=NYX-SAT-001/batch_<uuid>.jsonl)
def build_s3_object_key(*, prefix: str, satellite_id: str, timestamp: datetime, batch_id: str) -> str:
    ingestion_date = timestamp.strftime("%Y-%m-%d")

    return (f"{prefix}/"f"ingestion_date={ingestion_date}/"f"satellite_id={satellite_id}/"f"batch_{batch_id}.jsonl")

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
    
# Lambda entry point (writing to S3)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    bucket_name = os.environ["NYX_BRONZE_BUCKET"]
    bronze_prefix = os.environ.get("NYX_BRONZE_PREFIX", "bronze/telemetry")

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
            "decoded_records": 0
        }
    
    satellite_id = str(decoded_records[0].get("satellite_id", "unknown"))
    timestamp = datetime.now(UTC)
    batch_id = str(uuid4())

    object_key = build_s3_object_key(
        prefix=bronze_prefix,
        satellite_id=satellite_id,
        timestamp=timestamp,
        batch_id=batch_id
    )

    jsonl_payload = "\n".join(json.dumps(record) for record in decoded_records) + "\n"

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=jsonl_payload.encode("utf-8"),
        ContentType="application/json"
    )

    LOGGER.info(
        "Write %s decoded records(s) to s3://%s/%s",
        len(decoded_records),
        bucket_name,
        object_key
    )

    return {
        "status": "success",
        "received_records": len(records),
        "decoded_records": len(decoded_records),
        "s3_bucket": bucket_name,
        "s3_key": object_key
    }
