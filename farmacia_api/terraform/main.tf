terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 🔹 VPC por defecto
data "aws_vpc" "default" {
  default = true
}

# 🔹 Subnets de la VPC por defecto
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# 🔹 AMI Ubuntu 22.04 (LTS)
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# 🔐 Security Group
resource "aws_security_group" "farmacia_sg" {
  name        = "farmacia-sg"
  description = "Permite SSH, microservicios (5001-5003) y MongoDB opcional"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH acceso remoto"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.open_to_world ? "0.0.0.0/0" : var.my_ip_cidr]
  }

  ingress {
    description = "Microservicios Farmacia (catalog, inventory, orders)"
    from_port   = 5001
    to_port     = 5003
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "MongoDB (solo para pruebas internas)"
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  egress {
    description = "Permitir todo tráfico saliente"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "farmacia-sg"
  }
}

# 🚀 EC2: Servidor Tienda con Docker + microservicios
resource "aws_instance" "farmacia_api" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.farmacia_sg.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    set -eux
    export DEBIAN_FRONTEND=noninteractive

    # 🔧 Actualizar sistema e instalar dependencias
    apt-get update -y
    apt-get install -y python3-pip docker.io git curl

    # 🐳 Instalar Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # 🔑 Habilitar Docker y agregar usuario 'ubuntu'
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu

    # 📁 Clonar el repositorio con el proyecto
    cd /home/ubuntu
    git clone ${var.repo_url} farmacia_api
    cd farmacia_api

    # 🗃️ Crear volumen persistente para MongoDB
    mkdir -p data/db
    chmod -R 777 data/db

    # 🚀 Levantar todos los servicios
    /usr/local/bin/docker-compose up -d
  EOF

  tags = {
    Name = "farmacia_api"
  }
}