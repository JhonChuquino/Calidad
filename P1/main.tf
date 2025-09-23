terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.13"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------- IAM (rol y políticas) ----------
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "ms-basic-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

# Permisos básicos para escribir logs en CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_basic_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ---------- Empaquetar código ----------
data "archive_file" "productos_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_productos"
  output_path = "${path.module}/lambda_productos.zip"
}

data "archive_file" "resenas_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_resenas"
  output_path = "${path.module}/lambda_resenas.zip"
}

# ---------- Lambda: productos ----------
resource "aws_lambda_function" "productos" {
  function_name = "productos-ms"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.productos_zip.output_path
  source_code_hash = data.archive_file.productos_zip.output_base64sha256
  timeout       = 10
}

# ---------- API HTTP para productos ----------
resource "aws_apigatewayv2_api" "productos_api" {
  name          = "productos-http-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "productos_integration" {
  api_id                 = aws_apigatewayv2_api.productos_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.productos.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "productos_route" {
  api_id    = aws_apigatewayv2_api.productos_api.id
  route_key = "GET /products"
  target    = "integrations/${aws_apigatewayv2_integration.productos_integration.id}"
}

resource "aws_apigatewayv2_stage" "productos_stage" {
  api_id      = aws_apigatewayv2_api.productos_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw_invoke_productos" {
  statement_id  = "AllowAPIGatewayInvokeProductos"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.productos.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.productos_api.execution_arn}/*/*"
}

# ---------- Lambda: reseñas (consume productos) ----------
resource "aws_lambda_function" "resenas" {
  function_name = "resenas-ms"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.resenas_zip.output_path
  source_code_hash = data.archive_file.resenas_zip.output_base64sha256
  timeout       = 10

  environment {
    variables = {
      # URL completa hacia el endpoint GET /products del otro microservicio
      PRODUCTS_API_URL = "${aws_apigatewayv2_api.productos_api.api_endpoint}/products"
    }
  }

  depends_on = [aws_apigatewayv2_stage.productos_stage]
}

# ---------- API HTTP para reseñas ----------
resource "aws_apigatewayv2_api" "resenas_api" {
  name          = "resenas-http-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "resenas_integration" {
  api_id                 = aws_apigatewayv2_api.resenas_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.resenas.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "resenas_route" {
  api_id    = aws_apigatewayv2_api.resenas_api.id
  route_key = "POST /reviews"
  target    = "integrations/${aws_apigatewayv2_integration.resenas_integration.id}"
}

resource "aws_apigatewayv2_stage" "resenas_stage" {
  api_id      = aws_apigatewayv2_api.resenas_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw_invoke_resenas" {
  statement_id  = "AllowAPIGatewayInvokeResenas"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resenas.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.resenas_api.execution_arn}/*/*"
}
