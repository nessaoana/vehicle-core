#!/usr/bin/env bash
# Publica o vehicle-core no cluster atual do kubectl.
# Uso: scripts/deploy.sh [tag-da-imagem]
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NAMESPACE="vehicle-core"
IMAGE_TAG="${1:-${IMAGE_TAG:-main}}"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-${DOCKERHUB_USERNAME:-nessaoana}/vehicle-core}"
POSTGRES_USER="${CORE_POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${CORE_POSTGRES_PASSWORD:-postgres}"

# Copia os manifestos para não alterar o kustomization.yaml versionado.
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT
cp "${ROOT_DIR}"/k8s/*.yaml "${WORK_DIR}/"
(cd "${WORK_DIR}" && kustomize edit set image "vehicle-core-api=${IMAGE_REPOSITORY}:${IMAGE_TAG}")

kubectl apply -f "${ROOT_DIR}/k8s/namespace.yaml"
kubectl -n "${NAMESPACE}" create secret generic vehicle-core-db \
  --from-literal=POSTGRES_USER="${POSTGRES_USER}" \
  --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -k "${WORK_DIR}"
kubectl -n "${NAMESPACE}" rollout status statefulset/vehicle-core-db --timeout=300s
kubectl -n "${NAMESPACE}" rollout status deployment/vehicle-core-api --timeout=300s
kubectl -n "${NAMESPACE}" get pods,svc,hpa,ingress
