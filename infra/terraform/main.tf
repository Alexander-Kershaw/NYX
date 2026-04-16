locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  lambda_package_path = abspath("${path.module}/../../build/nyx_lambda_consumer.zip")
}

#===================================================================================================================

# NYX S3 Bronze bucket

#===================================================================================================================

resource "aws_s3_bucket" "nyx_bronze" {
  bucket = var.s3_bucket_name

  tags = merge(
    local.common_tags, {
      Name  = var.s3_bucket_name
      Layer = "bronze"
    }
  )
}

resource "aws_s3_bucket_versioning" "nyx_bronze_versioning" {
  bucket = aws_s3_bucket.nyx_bronze.id

  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "nyx_bronze_encryption" {
  bucket = aws_s3_bucket.nyx_bronze.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "nyx_bronze_public_access" {
  bucket = aws_s3_bucket.nyx_bronze.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#===================================================================================================================

# NYX Kinesis stream

#===================================================================================================================

resource "aws_kinesis_stream" "nyx_telemetry" {
  name             = var.kinesis_stream_name
  shard_count      = var.kinesis_shard_count
  retention_period = 24

  encryption_type = "KMS"
  kms_key_id      = "alias/aws/kinesis"

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  tags = merge(
    local.common_tags, {
      Name    = var.kinesis_stream_name
      Purpose = "telemetry-ingestion"
    }
  )
}

#===================================================================================================================

# NYX Lambda Execution Role

#===================================================================================================================

resource "aws_iam_role" "nyx_lambda_execution_role" {
  name = "${var.lambda_function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.lambda_function_name}-role"
    }
  )
}

resource "aws_iam_role_policy" "nyx_lambda_s3_kinesis_logs_policy" {
  name = "${var.lambda_function_name}-policy"
  role = aws_iam_role.nyx_lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Sid    = "AllowS3PutObject"
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.nyx_bronze.arn}/bronze/*",
          "${aws_s3_bucket.nyx_bronze.arn}/silver/*",
          "${aws_s3_bucket.nyx_bronze.arn}/quarantine/*"
        ]
      },
      {
        Sid    = "AllowKinesisRead"
        Effect = "Allow"
        Action = [
          "kinesis:DescribeStream",
          "kinesis:DescribeStreamSummary",
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:ListShards",
          "kinesis:SubscribeToShard"
        ]
        Resource = aws_kinesis_stream.nyx_telemetry.arn
      },
      {
        Sid    = "AllowSnsPublish"
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.nyx_operational_alerts.arn
      },
      {
        Sid    = "AllowCloudWatchMetrics"
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}


#===================================================================================================================

# NYX Lambda consumer

#===================================================================================================================

resource "aws_lambda_function" "nyx_bronze_landing_consumer" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.nyx_lambda_execution_role.arn
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime

  filename         = local.lambda_package_path
  source_code_hash = filebase64sha256(local.lambda_package_path)

  timeout     = var.lambda_timeout_seconds
  memory_size = var.lambda_memory_mb

  environment {
    variables = {
      NYX_BRONZE_BUCKET     = aws_s3_bucket.nyx_bronze.bucket
      NYX_BRONZE_PREFIX     = "bronze/telemetry"
      NYX_SILVER_PREFIX     = "silver/telemetry"
      NYX_QUARANTINE_PREFIX = "quarantine/telemetry"
      NYX_ALERT_TOPIC_ARN   = aws_sns_topic.nyx_operational_alerts.arn
    }
  }

  tags = merge(
    local.common_tags,
    {
      Name = var.lambda_function_name
    }
  )
}

resource "aws_lambda_event_source_mapping" "nyx_kinesis_to_lambda" {
  event_source_arn  = aws_kinesis_stream.nyx_telemetry.arn
  function_name     = aws_lambda_function.nyx_bronze_landing_consumer.arn
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true
}


#===================================================================================================================

# NYX Athena SQL Results Bucket

#===================================================================================================================

resource "aws_s3_bucket" "nyx_athena_results" {
  bucket = var.athena_bucket_name

  tags = merge(
    local.common_tags,
    {
      Name    = var.athena_bucket_name
      Purpose = "athena-query-results"
    }
  )
}

resource "aws_s3_bucket_versioning" "nyx_athena_results_versioning" {
  bucket = aws_s3_bucket.nyx_athena_results.id

  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "nyx_athena_results_encryption" {
  bucket = aws_s3_bucket.nyx_athena_results.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "nyx_athena_results_public_access" {
  bucket = aws_s3_bucket.nyx_athena_results.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


#===================================================================================================================

# NYX Glue Catalog Database

#===================================================================================================================

resource "aws_glue_catalog_database" "nyx_telemetry" {
  name = var.glue_database_name

  description = "Glue catalog database for NYX telemetry stream datasets"
}


#===================================================================================================================

# NYX Glue Catalog Table - Silver Telemetry

#===================================================================================================================

resource "aws_glue_catalog_table" "nyx_silver_telemetry" {
  name          = "silver_telemetry"
  database_name = aws_glue_catalog_database.nyx_telemetry.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL = "TRUE"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.nyx_bronze.bucket}/silver/telemetry/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat"

    # newline delimited JSON pattern
    ser_de_info {
      name                  = "nyx_silver_telemetry_json"
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }

    columns {
      name = "event_id"
      type = "string"
    }

    columns {
      name = "event_timestamp"
      type = "string"
    }

    columns {
      name = "satellite_id"
      type = "string"
    }

    columns {
      name = "ground_station_id"
      type = "string"
    }

    columns {
      name = "event_type"
      type = "string"
    }

    columns {
      name = "schema_version"
      type = "string"
    }

    columns {
      name = "source_ip"
      type = "string"
    }

    columns {
      name = "ingest_source"
      type = "string"
    }

    columns {
      name = "latitude"
      type = "double"
    }

    columns {
      name = "longitude"
      type = "double"
    }

    columns {
      name = "altitude_km"
      type = "double"
    }

    columns {
      name = "velocity_kms"
      type = "double"
    }

    columns {
      name = "battery_pct"
      type = "double"
    }

    columns {
      name = "temperature_c"
      type = "double"
    }

    columns {
      name = "signal_strength_db"
      type = "double"
    }

    columns {
      name = "uplink_latency_ms"
      type = "double"
    }

    columns {
      name = "downlink_latency_ms"
      type = "double"
    }

    columns {
      name = "packet_integrity_score"
      type = "double"
    }

    columns {
      name = "auth_status"
      type = "string"
    }

    columns {
      name = "payload_status"
      type = "string"
    }

    columns {
      name = "status_code"
      type = "string"
    }

    columns {
      name = "orbit_class"
      type = "string"
    }

    columns {
      name = "mission_mode"
      type = "string"
    }

    columns {
      name = "is_anomalous"
      type = "boolean"
    }

    columns {
      name = "anomaly_type"
      type = "string"
    }

    columns {
      name = "validated_at"
      type = "string"
    }
  }

  partition_keys {
    name = "ingestion_date"
    type = "string"
  }
}

#===================================================================================================================

# NYX SNS Alerting

#===================================================================================================================

resource "aws_sns_topic" "nyx_operational_alerts" {
  name = var.sns_topic_name

  tags = merge(
    local.common_tags,
    {
      Name    = var.sns_topic_name
      Purpose = "operational-alerting"
    }
  )
}

resource "aws_sns_topic_subscription" "nyx_alert_email_subscription" {
  topic_arn = aws_sns_topic.nyx_operational_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_address
}

#===================================================================================================================

# NYX Ingestion CloudWatch Dashboard

#===================================================================================================================

resource "aws_cloudwatch_dashboard" "nyx_operational_dashboard" {
  dashboard_name = var.cloudwatch_dashboard_name

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          title   = "NYX Ingestion - Events Received vs Decoded"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          stat    = "Sum"
          period  = 60

          metrics = [
            ["NYX/Ingestion", "ReceivedEvents"],
            [".", "DecodedEvents"]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          title   = "NYX Validation - Silver vs Quarantine"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          stat    = "Sum"
          period  = 60

          metrics = [
            ["NYX/Ingestion", "SilverEventsr"],
            [".", "QuarantineEvents"]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          title   = "NYX Alerts Published"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          stat    = "Sum"
          period  = 60

          metrics = [
            ["NYX/Ingestion", "AlertsPublished"]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          title   = "NYX Lambda Invocations and Errors"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          stat    = "Sum"
          period  = 60

          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.nyx_bronze_landing_consumer.function_name],
            [".", "Errors", ".", "."]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 24
        height = 6

        properties = {
          title   = "NYX Lambda Duration"
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          stat    = "Average"
          period  = 60

          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.nyx_bronze_landing_consumer.function_name]
          ]
        }
      }
    ]
  })
}


#===================================================================================================================

# S3 Storage Lifecycle (Bronze/Silver/Quarantine)

#===================================================================================================================

resource "aws_s3_bucket_lifecycle_configuration" "nyx_bronze_lifecycle" {
  bucket = aws_s3_bucket.nyx_bronze.id

  rule {
    id     = "bronze-retention"
    status = "Enabled"

    filter {
      prefix = "bronze/"
    }

    expiration {
      days = var.bronze_retention_days
    }
  }

  rule {
    id     = "silver-retention"
    status = "Enabled"

    filter {
      prefix = "silver/"
    }

    expiration {
      days = var.silver_retention_days
    }
  }

  rule {
    id     = "quarantine-retention"
    status = "Enabled"

    filter {
      prefix = "quarantine/"
    }

    expiration {
      days = var.quarantine_retention_days
    }
  }
}


#===================================================================================================================

# S3 Storage Lifecycle (Athena Query Results)

#===================================================================================================================

resource "aws_s3_bucket_lifecycle_configuration" "nyx_athena_results_encryption_lifecycle" {
  bucket = aws_s3_bucket.nyx_athena_results.id

  rule {
    id     = "athena-results-retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = var.athena_retention_days
    }
  }
}