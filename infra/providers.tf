terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # O state fica num bucket do próprio LocalStack e é salvo junto com o Cloud Pod,
  # para que cada execução do CD reconheça o cluster já existente.
  backend "s3" {
    bucket                      = "vehicle-terraform-state"
    key                         = "vehicle-platform/terraform.tfstate"
    region                      = "us-east-1"
    access_key                  = "test"
    secret_key                  = "test"
    use_path_style              = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_region_validation      = true

    endpoints = {
      s3 = "http://localhost:4566"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = var.aws_access_key
  secret_key                  = var.aws_secret_key
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true

  endpoints {
    apigatewayv2 = var.localstack_endpoint
    ec2          = var.localstack_endpoint
    eks          = var.localstack_endpoint
    iam          = var.localstack_endpoint
    sts          = var.localstack_endpoint
  }
}
