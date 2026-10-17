# Infraestrutura local: LocalStack Pro + EKS + API Gateway.
# Pré-requisitos: docker, terraform, aws cli, kubectl, kustomize, jq.

LOCALSTACK_ENDPOINT ?= http://localhost:4566
IMAGE_TAG ?= main
AWS_LOCAL = AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=$(LOCALSTACK_ENDPOINT) --region us-east-1
GATEWAY_URL = $$(terraform -chdir=infra output -raw api_gateway_url)

.PHONY: localstack cluster deploy gateway-url smoke-test e2e-test load-test destroy

localstack: ## Sobe o LocalStack Pro
	docker compose --profile cluster up -d --wait localstack

cluster: ## Cria o cluster EKS e o API Gateway via Terraform e configura o kubectl
	$(AWS_LOCAL) s3 mb s3://vehicle-terraform-state 2>/dev/null || true
	terraform -chdir=infra init -input=false
	terraform -chdir=infra apply -input=false -auto-approve
	LOCALSTACK_ENDPOINT=$(LOCALSTACK_ENDPOINT) scripts/kubeconfig.sh

deploy: ## Publica o vehicle-core no cluster
	scripts/deploy.sh $(IMAGE_TAG)

gateway-url: ## Mostra a URL pública do API Gateway
	@terraform -chdir=infra output -raw api_gateway_url; echo

smoke-test: ## Testa as rotas do vehicle-core pelo API Gateway
	scripts/smoke-test.sh $(GATEWAY_URL)

e2e-test: ## Fluxo completo (core + sales já publicados) pelo API Gateway
	E2E_BASE_URL=$(GATEWAY_URL) .venv/bin/pytest e2e -v

load-test: ## Carga para demonstrar o HPA (acompanhe com: kubectl get hpa -A -w)
	scripts/load-test.sh $(GATEWAY_URL)

destroy: ## Remove o cluster e o API Gateway
	terraform -chdir=infra destroy -input=false -auto-approve
