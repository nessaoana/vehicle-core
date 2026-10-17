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

variable "environment" {
  description = "Nome do ambiente usado nas tags."
  type        = string
  default     = "localstack"
}

variable "cluster_name" {
  description = "Nome do cluster EKS compartilhado pelos serviços."
  type        = string
  default     = "vehicle-cluster"
}

variable "ingress_endpoint" {
  description = "URL do load balancer do Ingress (Traefik) do cluster, vista a partir do container do LocalStack."
  type        = string
  default     = "http://host.docker.internal:8081"
}

variable "frontend_origins" {
  description = "Origens liberadas no CORS do API Gateway."
  type        = list(string)
  default     = ["http://localhost:3000", "http://localhost:5173"]
}

variable "gateway_rate_limit" {
  description = "Requisições por segundo permitidas por rota no API Gateway."
  type        = number
  default     = 100
}

variable "gateway_burst_limit" {
  description = "Rajada máxima de requisições por rota no API Gateway."
  type        = number
  default     = 200
}
