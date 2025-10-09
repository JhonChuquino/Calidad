# Dirección IP pública
output "farmacia_public_ip" {
  value = aws_instance.api_tienda.public_ip
}

# URL de prueba para verificar el catálogo
output "farmacia_catalog_test_url" {
  value = "http://${aws_instance.tienda_api.public_ip}:5001/catalog"
}

# URL de prueba para crear una orden
output "farmacia_order_test_url" {
  value = "http://${aws_instance.api_tienda.public_ip}:5003/orders"
}

# Comando SSH de acceso rápido
output "ssh_hint" {
  value = "ssh -i nube.pem ec2-user@${aws_instance.api_tienda.public_ip}"
}
