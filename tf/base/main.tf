terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.45"
    }
  }

  backend "s3" {
    bucket         = "dlplatform-dev-terraform-remote-state-storage"
    key            = "dl_web/base/state.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "DLPlatform-Dev-terraform-state-lock-dynamo"
  }

  required_version = ">= 1.0.0"
}

variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

variable "aws_vault_profile" {
  type    = string
  default = "dl-dev"
}

variable "aws_app_account_id" {
  type    = number
  default = 955696714113
}

provider "aws" {
  profile = var.aws_vault_profile
  region  = var.aws_region

  assume_role {
    role_arn = "arn:aws:iam::${var.aws_app_account_id}:role/developer"
  }
}

resource "aws_vpc" "dl_web_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  instance_tenancy     = "default"
  tags                 = { Name = "dl-web-vpc" }
}

resource "aws_internet_gateway" "dl_web_gw" {
  vpc_id = aws_vpc.dl_web_vpc.id
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "public" {
  count                   = length(data.aws_availability_zones.available.names)
  vpc_id                  = aws_vpc.dl_web_vpc.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags                    = { Tier = "Public" }
}
resource "aws_subnet" "private" {
  count                   = length(data.aws_availability_zones.available.names)
  vpc_id                  = aws_vpc.dl_web_vpc.id
  cidr_block              = "10.0.${10 + count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false
  tags                    = { Tier = "Private" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.dl_web_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.dl_web_gw.id
  }
}

resource "aws_route_table_association" "route_table_association" {
  for_each = toset(aws_subnet.public.*.id)

  subnet_id      = each.value
  route_table_id = aws_route_table.public.id
}

# resource "aws_route53_zone" "dl_web_dns_zone" {
#     name         = "digital-land.info"
# }

# resource "aws_route53_record" "dl_web_dns_record" {
#     name    = "www.test.digital-land.info"
#     type    = "A"
#     zone_id = aws_route53_zone.dl_web_dns_zone.id

#     alias {
#         evaluate_target_health = true
#         name                   = aws_lb.dl_web_lb.dns_name
#         zone_id                = aws_lb.dl_web_lb.zone_id
#     }
# }

# if we let terraform manage ECR, we lost all images on destroy
# resource "aws_ecr_repository" "dl_web_ecr" {
#     image_tag_mutability = "MUTABLE"
#     name                 = "dl-web"
# }

resource "aws_lb" "dl_web_lb" {
  name               = "dl-web-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.dl_web_lb_sg.id]
  subnets            = aws_subnet.public.*.id

  depends_on = [aws_internet_gateway.dl_web_gw]

  # access_logs {
  #   bucket  = aws_s3_bucket.lb_logs.bucket
  #   prefix  = "test-lb"
  #   enabled = true
  # }
}

# output "load_balancer_dns" {
#     value = aws_lb.dl_web_lb.dns_name
# }

# data "aws_ecs_container_definition" "dl_web" {
#   task_definition = aws_ecs_task_definition.dl_web_task.id
#   container_name  = "dl-web"
# }

# resource "aws_lb_target_group_attachment" "dl_web_lb_target_group_attachement" {
#   target_group_arn = aws_lb_target_group.dl_web_lb_target_group.id
#   target_id        = data.aws_ecs_container_definition.dl_web.id
#   port             = 80
# }

resource "aws_security_group" "dl_web_lb_sg" {
  description = "Load Balancer Allowed Ports"
  egress = [
    {
      cidr_blocks = [
        "0.0.0.0/0",
      ]
      description      = "Allow egress to ECS instance security group"
      from_port        = 32768
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      self             = false
      to_port          = 65535
      security_groups = [
        aws_security_group.ecs_instance_sg.id
      ]
    },
  ]
  ingress = [
    {
      cidr_blocks = [
        "0.0.0.0/0",
      ]
      description      = ""
      from_port        = 80
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 80
    },
    {
      cidr_blocks = [
        "0.0.0.0/0",
      ]
      description      = ""
      from_port        = 443
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 443
    }
  ]
  name     = "dl_web_lb_sg"
  tags     = {}
  tags_all = {}
  vpc_id   = aws_vpc.dl_web_vpc.id

  timeouts {}
}

# this rule depends on both security groups so separating it allows it
# to be created after both
resource "aws_security_group_rule" "lb_ingress" {
  security_group_id        = aws_security_group.ecs_instance_sg.id
  description              = "ephemeral port range for Load Balancer ingress"
  from_port                = 32768
  to_port                  = 65535
  protocol                 = "tcp"
  type                     = "ingress"
  source_security_group_id = aws_security_group.dl_web_lb_sg.id
}

resource "aws_security_group_rule" "all_egress" {
  security_group_id = aws_security_group.ecs_instance_sg.id
  description       = "allow any egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  type              = "egress"
  cidr_blocks = [
    "0.0.0.0/0",
  ]
}

resource "aws_security_group_rule" "ssh_ingress" {
  security_group_id = aws_security_group.ecs_instance_sg.id
  description       = "allow ssh access to ECS instances"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  type              = "ingress"
  cidr_blocks = [
    "0.0.0.0/0",
  ]
}

resource "aws_security_group" "ecs_instance_sg" {
  description = "ECS instance security group"
  name        = "dl_web_ecs_instance_sg"
  vpc_id      = aws_vpc.dl_web_vpc.id
}

resource "aws_acm_certificate" "dl_web_acm_certificate" {
  domain_name               = "*.digital-land.info"
  subject_alternative_names = []
  tags                      = {}
  tags_all                  = {}
  validation_method         = "DNS"

  options {
    certificate_transparency_logging_preference = "ENABLED"
  }
}
