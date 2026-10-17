#!/usr/bin/env bash
# Aguarda o cluster EKS do LocalStack ficar ativo e configura o kubectl para usá-lo.
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-vehicle-cluster}"
AWS_REGION="${AWS_REGION:-us-east-1}"
LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT:-http://localhost:4566}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"

aws_local() {
  aws --endpoint-url="${LOCALSTACK_ENDPOINT}" --region "${AWS_REGION}" "$@"
}

echo "Aguardando o cluster ${CLUSTER_NAME} ficar ACTIVE..."
aws_local eks wait cluster-active --name "${CLUSTER_NAME}"
aws_local eks update-kubeconfig --name "${CLUSTER_NAME}"

echo "Aguardando os nós do Kubernetes..."
for _ in $(seq 1 60); do
  if kubectl wait --for=condition=Ready nodes --all --timeout=5s >/dev/null 2>&1; then
    kubectl get nodes
    exit 0
  fi
  sleep 5
done

echo "Os nós do cluster não ficaram prontos a tempo." >&2
exit 1
