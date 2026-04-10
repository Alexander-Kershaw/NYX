output "aws_region" {
    description = "AWS region configured for the NYX cloud infrastructure"
    value = var.aws_region
}

output "project_name" {
    description = "Project name used for NYX infrastructure"
    value = var.project_name
}

output "environment" {
    description = "Deployment environment used for the NYX cloud infrastructure"
    value = var.environment
}

output "s3_bucket_name" {
    description = "Configured S3 bucket name for NYX bronze data"
    value = var.s3_bucket_name
}

output "kinesis_stream_name" {
    description = "Configured Kinesis stream name"
    value = var.kinesis_stream_name
}

output "lambda_function_name" {
    description = "Configured Lambda function name"
    value = var.lambda_function_name
}

