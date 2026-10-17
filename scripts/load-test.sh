#!/usr/bin/env bash
# Gera carga na busca de veículos do vehicle-core para demonstrar o autoscaling.
# Em outro terminal: kubectl get hpa -A -w
# Uso: scripts/load-test.sh <api_gateway_url> [duração] [concorrência]
set -euo pipefail

BASE_URL="${1:?Informe a URL do API Gateway}"
DURATION="${2:-120s}"
CONCURRENCY="${3:-50}"

if ! command -v hey >/dev/null 2>&1; then
  echo "Instale o hey (brew install hey) para rodar o teste de carga." >&2
  exit 1
fi

hey -z "${DURATION}" -c "${CONCURRENCY}" "${BASE_URL%/}/vehicles"
