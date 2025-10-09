variable "aws_region" {
  default = "us-east-1"
}

variable "key_name" {
  default = "nube"
}

variable "repo_url" {
  default = "https://github.com/JhonChuquino/Calidad.git"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "open_to_world" {
  default = true
}

variable "my_ip_cidr" {
  default = "0.0.0.0/0"
}
