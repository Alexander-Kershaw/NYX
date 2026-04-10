locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

#===================================================================================================================

# NYX S3 Bronze bucket

#===================================================================================================================

resource "aws_s3_bucket" "NYX_bronze" {
  bucket = var.s3_bucket_name

  tags = merge(
    local.common_tags, {
      Name  = var.s3_bucket_name
      Layer = "bronze"
    }
  )
}

resource "aws_s3_bucket_versioning" "NYX_bronze_versioning" {
  bucket = aws_s3_bucket.NYX_bronze.id

  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "NYX_bronze_encryption" {
  bucket = aws_s3_bucket.NYX_bronze.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "NYX_bronze_public_access" {
  bucket = aws_s3_bucket.NYX_bronze.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#===================================================================================================================

# NYX Kinesis stream

#===================================================================================================================

resource "aws_kinesis_stream" "NYX_telemetry" {
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

# NYX Lambda consumer

#===================================================================================================================

