variable "aws_region" {
  description = "AWS region for NYX cloud infrastructure"
  type        = string
}

variable "project_name" {
  description = "Project name used for any tagging and naming"
  type        = string
  default     = "nyx"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Globally unique S3 bucket name for the NYX bronze layer data"
  type        = string
}

variable "kinesis_stream_name" {
  description = "Name of the Kinesis stream for the NYX telemetry ingestion"
  type        = string
  default     = "nyx-telemetry-stream"
}

variable "lambda_function_name" {
  description = "Name of the Lambda bronze landing consumer"
  type        = string
  default     = "nyx-bronze-landing_consumer"
}

variable "kinesis_shard_count" {
  description = "Shard count for the NYX telemetry Kinesis stream"
  type        = number
  default     = 1
}

variable "enable_s3_versioning" {
  description = "Enable/disable versioning on the NYX bronze bucket"
  type        = bool
  default     = true
}

