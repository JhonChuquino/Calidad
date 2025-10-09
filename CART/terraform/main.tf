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


data "aws_vpc" "default" {
  default = true
}


data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_security_group" "farmacia_sg" {
  name        = "farmacia-sg"
  description = "Permite SSH y microservicios 5001-5003"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Acceso SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.open_to_world ? "0.0.0.0/0" : var.my_ip_cidr]
  }

  ingress {
    description = "Microservicios Farmacia"
    from_port   = 5001
    to_port     = 5003
    protocol    = "tcp"
    cidr_blocks = [var.open_to_world ? "0.0.0.0/0" : var.my_ip_cidr]
  }

  egress {
    description = "Todo el trafico saliente permitido"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "farmacia-sg"
  }
}

resource "aws_instance" "api_tienda" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.farmacia_sg.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    set -eux

    # Actualizar sistema e instalar Docker y Git
    yum update -y
    yum install -y docker git
    systemctl enable docker
    systemctl start docker

    # Instalar Docker Compose (versión estable)
    curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Clonar el repositorio con la API de la Farmacia
    cd /home/ec2-user
    git clone ${var.repo_url}
    cd Calidad/api_tienda || cd Calidad

    # Crear volumen persistente para MongoDB
    mkdir -p data/db
    chmod -R 777 data/db

    # Levantar los microservicios
    /usr/local/bin/docker-compose up -d
  EOF

  tags = {
    Name = "api_tienda"
  }
}
