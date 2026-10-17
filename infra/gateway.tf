locals {
  # Somente as rotas listadas aqui ficam públicas. Rotas internas, como
  # PATCH /vehicles/{vehicle_id}/availability, e os health checks não são expostas.
  public_routes = {
    # vehicle-core
    "POST /vehicles"               = "/vehicles"
    "GET /vehicles"                = "/vehicles"
    "GET /vehicles/{vehicle_id}"   = "/vehicles/{vehicle_id}"
    "PATCH /vehicles/{vehicle_id}" = "/vehicles/{vehicle_id}"
    # vehicle-sales
    "GET /vehicles/available" = "/vehicles/available"
    "GET /vehicles/sold"      = "/vehicles/sold"
    "POST /sales"             = "/sales"
    "POST /payments/webhook"  = "/payments/webhook"
  }
}

resource "aws_apigatewayv2_api" "public" {
  name          = "vehicle-api"
  protocol_type = "HTTP"
  description   = "Porta de entrada pública das APIs vehicle-core e vehicle-sales."

  cors_configuration {
    allow_origins = var.frontend_origins
    allow_methods = ["GET", "POST", "PATCH", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 3600
  }

  tags = local.tags
}

resource "aws_apigatewayv2_integration" "public" {
  for_each = local.public_routes

  api_id             = aws_apigatewayv2_api.public.id
  integration_type   = "HTTP_PROXY"
  integration_method = split(" ", each.key)[0]
  integration_uri    = "${var.ingress_endpoint}${each.value}"
}

resource "aws_apigatewayv2_route" "public" {
  for_each = local.public_routes

  api_id    = aws_apigatewayv2_api.public.id
  route_key = each.key
  target    = "integrations/${aws_apigatewayv2_integration.public[each.key].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.public.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_rate_limit  = var.gateway_rate_limit
    throttling_burst_limit = var.gateway_burst_limit
  }

  tags = local.tags
}
