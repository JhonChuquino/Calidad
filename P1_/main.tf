terraform {
  required_version = ">= 1.6.0"
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

# VPC y subred por defecto
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# AMI Amazon Linux 2
data "aws_ami" "al2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_security_group" "svc" {
  name_prefix = "clima-temblor-sg-"
  description = "Abrir puertos 8001 y 8002"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8002
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "svc" {
  ami                         = data.aws_ami.al2.id
  instance_type               = var.instance_type
  vpc_security_group_ids      = [aws_security_group.svc.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3
    pip3 install flask

    cat >/opt/app.py <<'PY'
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# Datos simulados de clima por ciudad
CLIMA_DATA = {
    "Huanuco": {"temp_c": 24, "condicion": "Soleado"},
    "Lima": {"temp_c": 19, "condicion": "Nublado"},
    "Cusco": {"temp_c": 12, "condicion": "Frío"},
    "Arequipa": {"temp_c": 16, "condicion": "Despejado"}
}

# Datos simulados de temblor por ciudad
TEMBLOR_DATA = {
    "Huanuco": {"probabilidad": 0.08, "intensidad": "III-IV"},
    "Lima": {"probabilidad": 0.12, "intensidad": "IV"},
    "Cusco": {"probabilidad": 0.05, "intensidad": "II-III"},
    "Arequipa": {"probabilidad": 0.10, "intensidad": "III"}
}

@app.get("/clima")
def clima():
    fecha = request.args.get("fecha", "2025-09-23")
    ciudad = request.args.get("ciudad", "Huanuco")
    datos = CLIMA_DATA.get(ciudad, {"temp_c": None, "condicion": "No disponible"})
    return jsonify({
        "servicio": "clima",
        "fecha": fecha,
        "ciudad": ciudad,
        **datos
    })

@app.get("/temblor")
def temblor():
    fecha = request.args.get("fecha", "2025-09-23")
    ciudad = request.args.get("ciudad", "Huanuco")
    datos = TEMBLOR_DATA.get(ciudad, {"probabilidad": None, "intensidad": "No disponible"})
    return jsonify({
        "servicio": "temblor",
        "fecha": fecha,
        "ciudad": ciudad,
        **datos
    })

if __name__=="__main__":
    from threading import Thread
    def run1(): app.run(host="0.0.0.0", port=8001)
    def run2(): app.run(host="0.0.0.0", port=8002)
    Thread(target=run1).start()
    Thread(target=run2).start()

PY

    cat >/etc/systemd/system/misservicios.service <<'UNIT'
[Unit]
Description=Clima y Temblor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/app.py
Restart=always
User=root
WorkingDirectory=/opt

[Install]
WantedBy=multi-user.target
UNIT

    systemctl daemon-reload
    systemctl enable misservicios
    systemctl start misservicios
  EOF
}
