#!/usr/bin/env bash
# Teste do vehicle-core pelo API Gateway: cadastra, edita, consulta e busca um
# veículo, e confere que a rota interna não está exposta. Não depende do
# vehicle-sales; o fluxo de compra entre os dois serviços fica em make e2e-test.
# Uso: scripts/smoke-test.sh <api_gateway_url>
set -euo pipefail

BASE_URL="${1:?Informe a URL do API Gateway}"
BASE_URL="${BASE_URL%/}"
# Placa no padrão Mercosul (ABC1D23) e marca únicas por execução.
SUFFIX="$(date +%s)"
LETTERS=(A B C D E F G H I J)
PLATE="TST${SUFFIX: -3:1}${LETTERS[${SUFFIX: -4:1}]}${SUFFIX: -2}"
BRAND="Smoke${SUFFIX}"

request() {
  local method="$1" path="$2" body="${3:-}"
  local args=(-sS --fail-with-body --retry 5 --retry-delay 3 --retry-connrefused -X "${method}" "${BASE_URL}${path}")
  if [ -n "${body}" ]; then
    args+=(-H 'Content-Type: application/json' -d "${body}")
  fi
  curl "${args[@]}"
}

echo "1. Cadastrando veículo ${PLATE}"
vehicle=$(request POST /vehicles "{\"license_plate\": \"${PLATE}\", \"brand\": \"${BRAND}\", \"model\": \"Corolla\", \"year\": 2024, \"price\": \"75000.00\", \"color\": \"Black\"}")
vehicle_id=$(echo "${vehicle}" | jq -r '.id')
echo "   id=${vehicle_id}"

echo "2. Editando o preço"
request PATCH "/vehicles/${vehicle_id}" '{"price": "72000.00"}' >/dev/null

echo "3. Consultando o veículo editado"
request GET "/vehicles/${vehicle_id}" | jq -e '(.price | tonumber) == 72000' >/dev/null

echo "4. Buscando pela marca"
request GET "/vehicles?brand=${BRAND}" | jq -e --argjson id "${vehicle_id}" 'map(.id) | index($id) != null' >/dev/null

echo "5. Conferindo que a rota interna não está exposta no gateway"
status=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH "${BASE_URL}/vehicles/${vehicle_id}/availability" \
  -H 'Content-Type: application/json' -d '{"status": "available", "active": true}')
if [ "${status}" != "404" ]; then
  echo "   esperado 404, recebido ${status}" >&2
  exit 1
fi

echo "Smoke test concluído com sucesso."
