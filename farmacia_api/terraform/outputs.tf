output "farmacia_api_public_ip" {
  description = "Dirección IP pública del servidor de la tienda"
  value       = aws_instance.farmacia_api.public_ip
}