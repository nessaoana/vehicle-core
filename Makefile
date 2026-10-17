# Infraestrutura local: LocalStack Pro + EKS + API Gateway.
# Pré-requisitos: docker, terraform, aws cli, kubectl, kustomize, jq.

LOCALSTACK_ENDPOINT ?= http://localhost:4566
IMAGE_TAG ?= main
SALES_DIR ?= ../vehicle-sales
AWS_LOCAL = AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=$(LOCALSTACK_ENDPOINT) --region us-east-1
GATEWAY_URL = $$(terraform -chdir=infra output -raw api_gateway_url)

.PHONY: localstack cluster deploy deploy-all gateway-url smoke-test load-test destroy

localstack: ## Sobe o LocalStack Pro
	docker compose --profile cluster up -d --wait localstack

cluster: ## Cria o cluster EKS e o API Gateway via Terraform e configura o kubectl
	$(AWS_LOCAL) s3 mb s3://vehicle-terraform-state 2>/dev/null || true
	terraform -chdir=infra init -input=false
	terraform -chdir=infra apply -input=false -auto-approve
	LOCALSTACK_ENDPOINT=$(LOCALSTACK_ENDPOINT) scripts/kubeconfig.sh

deploy: ## Publica o vehicle-core no cluster
	scripts/deploy.sh $(IMAGE_TAG)

deploy-all: deploy ## Publica o vehicle-core e o vehicle-sales
	$(SALES_DIR)/scripts/deploy.sh $(IMAGE_TAG)

gateway-url: ## Mostra a URL pública do API Gateway
	@terraform -chdir=infra output -raw api_gateway_url; echo

smoke-test: ## Fluxo ponta a ponta pelo API Gateway
	scripts/smoke-test.sh $(GATEWAY_URL)

load-test: ## Carga para demonstrar o HPA (acompanhe com: kubectl get hpa -A -w)
	scripts/load-test.sh $(GATEWAY_URL)

destroy: ## Remove o cluster e o API Gateway
	terraform -chdir=infra destroy -input=false -auto-approve
