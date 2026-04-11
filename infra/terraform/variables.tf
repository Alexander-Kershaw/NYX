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

variable "lambda_runtime" {
  description = "Runtime for the NYX Lambda consumer"
  type        = string
  default     = "python3.11"
}

variable "lambda_handler" {
  description = "Handler for the NYX Lambda consumer"
  type        = string
  default     = "cloud.lambda_consumer.lambda_handler"
}

variable "lambda_package_path" {
  description = "Path to the packaged Lambda zip file"
  type        = string
  default     = "../../build/nyx_lambda_consumer.zip"
}

variable "lambda_timeout_seconds" {
  description = "Timeout in seconds for the NYX Lambda consumer"
  type        = number
  default     = 30
}

variable "lambda_memory_mb" {
  description = "Memory size in MB for the NYX Lambda consumer"
  type        = number
  default     = 256
}
