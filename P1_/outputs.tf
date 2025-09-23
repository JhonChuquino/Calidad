output "clima_url" {
  value = "http://${aws_instance.svc.public_dns}:8001/clima"
}

output "temblor_url" {
  value = "http://${aws_instance.svc.public_dns}:8002/temblor"
}
