output "assets_bucket_name" {
  description = "Nome do bucket S3 provisionado."
  value       = aws_s3_bucket.assets.bucket
}

output "localstack_endpoint" {
  description = "Endpoint do LocalStack usado pelo Terraform."
  value       = var.localstack_endpoint
}