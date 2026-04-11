locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  lambda_package_path = abspath("${path.module}/../../build/nyx_telemetry_consumer.zip")
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
        Resource = "${aws_s3_bucket.nyx_bronze.arn}/*"
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
      NYX_BRONZE_BUCKET = aws_s3_bucket.nyx_bronze.bucket
      NYX_BRONZE_PREFIX = "bronze/telemetry"
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

