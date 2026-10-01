variable "aws_region" {
  description = "Região AWS usada pelo LocalStack."
  type        = string
  default     = "us-east-1"
}

variable "localstack_endpoint" {
  description = "Endpoint de borda do LocalStack."
  type        = string
  default     = "http://localhost:4566"
}

variable "aws_access_key" {
  description = "Chave de acesso compatível com AWS usada pelo LocalStack."
  type        = string
  default     = "test"
}

variable "aws_secret_key" {
  description = "Chave secreta compatível com AWS usada pelo LocalStack."
  type        = string
  default     = "test"
  sensitive   = true
}

variable "assets_bucket_name" {
  description = "Bucket S3 usado pelo vehicle-core."
  type        = string
  default     = "vehicle-core-assets"
}