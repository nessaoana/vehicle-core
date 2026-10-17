#!/usr/bin/env bash
# Teste ponta a ponta pelo API Gateway: cadastra um veículo (core), compra
# (sales), confirma o pagamento pelo webhook e confere a listagem de vendidos.
# Uso: scripts/smoke-test.sh <api_gateway_url>
set -euo pipefail

BASE_URL="${1:?Informe a URL do API Gateway}"
BASE_URL="${BASE_URL%/}"
# Placa no padrão Mercosul (ABC1D23) única por execução.
SUFFIX="$(date +%s)"
LETTERS=(A B C D E F G H I J)
PLATE="TST${SUFFIX: -3:1}${LETTERS[${SUFFIX: -4:1}]}${SUFFIX: -2}"

request() {
  local method="$1" path="$2" body="${3:-}"
  local args=(-sS --fail-with-body --retry 5 --retry-delay 3 --retry-connrefused -X "${method}" "${BASE_URL}${path}")
  if [ -n "${body}" ]; then
    args+=(-H 'Content-Type: application/json' -d "${body}")
  fi
  curl "${args[@]}"
}

echo "1. Cadastrando veículo ${PLATE} no vehicle-core"
vehicle=$(request POST /vehicles "{\"license_plate\": \"${PLATE}\", \"brand\": \"Toyota\", \"model\": \"Corolla\", \"year\": 2024, \"price\": \"75000.00\", \"color\": \"Black\"}")
vehicle_id=$(echo "${vehicle}" | jq -r '.id')
echo "   id=${vehicle_id}"

echo "2. Conferindo a listagem de veículos à venda (vehicle-sales)"
request GET /vehicles/available | jq -e --argjson id "${vehicle_id}" 'map(.id) | index($id) != null' >/dev/null

echo "3. Comprando o veículo"
sale=$(request POST /sales "{\"vehicle_id\": ${vehicle_id}, \"buyer_cpf\": \"529.982.247-25\"}")
payment_code=$(echo "${sale}" | jq -r '.payment_code')
echo "   payment_code=${payment_code}"

echo "4. Confirmando o pagamento pelo webhook"
request POST /payments/webhook "{\"payment_code\": \"${payment_code}\", \"status\": \"paid\"}" >/dev/null

echo "5. Conferindo a listagem de vendidos"
request GET /vehicles/sold | jq -e --argjson id "${vehicle_id}" 'map(.id) | index($id) != null' >/dev/null

echo "6. Conferindo que a rota interna não está exposta no gateway"
status=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH "${BASE_URL}/vehicles/${vehicle_id}/availability" \
  -H 'Content-Type: application/json' -d '{"status": "available"}')
if [ "${status}" != "404" ]; then
  echo "   esperado 404, recebido ${status}" >&2
  exit 1
fi

echo "Smoke test concluído com sucesso."
