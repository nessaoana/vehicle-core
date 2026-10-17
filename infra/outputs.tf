output "cluster_name" {
  description = "Nome do cluster EKS."
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "Endpoint da API do Kubernetes."
  value       = aws_eks_cluster.main.endpoint
}

output "api_gateway_url" {
  description = "URL base pública das APIs (usar no frontend)."
  value       = "http://${aws_apigatewayv2_api.public.id}.execute-api.localhost.localstack.cloud:4566"
}

output "api_gateway_id" {
  description = "ID do API Gateway."
  value       = aws_apigatewayv2_api.public.id
}
