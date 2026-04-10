output "aws_region" {
  description = "AWS region configured for the NYX cloud infrastructure"
  value       = var.aws_region
}

output "project_name" {
  description = "Project name used for NYX infrastructure"
  value       = var.project_name
}

output "environment" {
  description = "Deployment environment used for the NYX cloud infrastructure"
  value       = var.environment
}

output "s3_bucket_name" {
  description = "Configured S3 bucket name for NYX bronze data"
  value       = aws_s3_bucket.NYX_bronze.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the NYX bronze S3 bucket"
  value       = aws_s3_bucket.NYX_bronze.arn
}

output "kinesis_stream_name" {
  description = "NYX telemetry Kinesis stream name"
  value       = aws_kinesis_stream.NYX_telemetry.name
}

output "kinesis_shard_arn" {
  description = "ARN of the NYX telemetry Kinesis stream"
  value       = aws_kinesis_stream.NYX_telemetry.arn
}

