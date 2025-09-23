output "productos_url" {
  value = "${aws_apigatewayv2_api.productos_api.api_endpoint}/products"
}

output "resenas_url" {
  value = "${aws_apigatewayv2_api.resenas_api.api_endpoint}/reviews"
}
