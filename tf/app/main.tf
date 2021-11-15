terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.45"
    }
  }

  backend "s3" {
    bucket         = "dlplatform-dev-terraform-remote-state-storage"
    key            = "dl_web/app/state.tfstate"
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

# use remote state to access outputs from the base terraform configuration
data "terraform_remote_state" "base" {
  backend = "s3"

  config = {
    bucket         = "dlplatform-dev-terraform-remote-state-storage"
    key            = "dl_web/base/state.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "DLPlatform-Dev-terraform-state-lock-dynamo"
  }
}

# tf does not provision ECR so as to ensure we preserve our image history
data "aws_ecr_repository" "dl_web_ecr" {
  name = "dl-web"
}

resource "aws_iam_policy" "digital_land_collection_s3" {
  description = "A policy to allow read and write access to the collection-dataset s3 bucket."
  name        = "dl-web-policy-collection-s3"
  path        = "/"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "s3:ListBucket",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:s3:::collection-dataset",
          ]
        },
        {
          Action = [
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:s3:::collection-dataset/*",
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_iam_policy" "ecs_cloudwatch_logs" {
  description = "Allows ECS to log to CloudWatch"
  name        = "dl-web-policy-CloudWatchLogs"
  path        = "/"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "logs:DescribeLogStreams",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:logs:*:*:*",
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )
}


resource "aws_iam_role" "dl_app_role" {
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = [
              "ec2.amazonaws.com",
              "ecs.amazonaws.com",
              "ecs-tasks.amazonaws.com",
            ]
          }
          Sid = ""
        },
      ]
      Version = "2012-10-17"
    }
  )
  force_detach_policies = false
  managed_policy_arns = [
    aws_iam_policy.digital_land_collection_s3.arn,
    aws_iam_policy.ecs_cloudwatch_logs.arn,
    "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role",
  ]
  max_session_duration = 3600
  name                 = "DLPlatform-Dev-application"
  path                 = "/"
  tags                 = {}
  tags_all             = {}

  inline_policy {}
}

resource "aws_ecs_cluster" "dl_web_cluster" {
  capacity_providers = []
  name               = "dl-web-cluster"
  tags               = {}
  tags_all           = {}

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_cloudwatch_log_group" "dl_web_log_group" {
  name = "/ecs/dl-web"
}

resource "aws_ecs_task_definition" "dl_web_task" {
  container_definitions = jsonencode(
    [
      {
        cpu         = 0
        environment = []
        essential   = true
        image       = "${data.aws_ecr_repository.dl_web_ecr.repository_url}:latest"
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.dl_web_log_group.name
            awslogs-region        = "eu-west-2"
            awslogs-stream-prefix = "ecs"
          }
        }
        mountPoints = []
        name        = "dl-web"
        portMappings = [
          {
            containerPort = 80
            hostPort      = 0
            protocol      = "tcp"
          },
        ]
        volumesFrom = []
      },
    ]
  )
  cpu                = "1024"
  execution_role_arn = aws_iam_role.dl_app_role.arn
  family             = "dl-web"
  memory             = "1024"
  requires_compatibilities = [
    "EC2",
  ]
  tags          = {}
  tags_all      = {}
  task_role_arn = aws_iam_role.dl_app_role.arn
}

resource "aws_ecs_service" "dl_web_service" {
  cluster                            = aws_ecs_cluster.dl_web_cluster.arn
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  desired_count                      = 2
  enable_ecs_managed_tags            = true
  enable_execute_command             = false
  health_check_grace_period_seconds  = 120
  launch_type                        = "EC2"
  name                               = "dl-web-service"
  scheduling_strategy                = "REPLICA"
  tags                               = {}
  tags_all                           = {}
  task_definition                    = aws_ecs_task_definition.dl_web_task.arn

  deployment_circuit_breaker {
    enable   = false
    rollback = false
  }

  deployment_controller {
    type = "ECS"
  }

  load_balancer {
    container_name   = "dl-web"
    container_port   = 80
    target_group_arn = aws_lb_target_group.dl_web_lb_target_group.arn
  }

  ordered_placement_strategy {
    field = "attribute:ecs.availability-zone"
    type  = "spread"
  }
  ordered_placement_strategy {
    field = "instanceId"
    type  = "spread"
  }

  timeouts {}
}

resource "aws_lb_target_group" "dl_web_lb_target_group" {
  deregistration_delay          = 10
  load_balancing_algorithm_type = "round_robin"
  name                          = "dl-web-lb-target-group"
  port                          = 80
  protocol                      = "HTTP"
  protocol_version              = "HTTP1"
  slow_start                    = 0
  tags                          = {}
  tags_all                      = {}
  target_type                   = "instance"
  vpc_id                        = data.terraform_remote_state.base.outputs.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 5
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  stickiness {
    cookie_duration = 86400
    enabled         = false
    type            = "lb_cookie"
  }
}

resource "aws_lb_listener" "dl_web_lb_listener" {
  load_balancer_arn = data.terraform_remote_state.base.outputs.load_balancer_arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "dl_web_lb_listener_https" {
  certificate_arn   = data.terraform_remote_state.base.outputs.certificate_arn
  load_balancer_arn = data.terraform_remote_state.base.outputs.load_balancer_arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  tags              = {}
  tags_all          = {}

  default_action {
    order            = 1
    target_group_arn = aws_lb_target_group.dl_web_lb_target_group.arn
    type             = "forward"
  }

  timeouts {}
}

resource "aws_launch_configuration" "ecs_launch_config" {
  associate_public_ip_address = true
  ebs_optimized               = false
  enable_monitoring           = true
  iam_instance_profile        = "arn:aws:iam::955696714113:instance-profile/ecsInstanceRole"
  image_id                    = "ami-05db1ea966500fa94"
  instance_type               = "t2.medium"
  key_name                    = "jb-test"
  name                        = "dl_web_launch_config"
  security_groups = [
    data.terraform_remote_state.base.outputs.ecs_instance_sg_id
  ]
  user_data = <<-USERDATA
                                       #!/bin/bash
                                       echo ECS_CLUSTER=${aws_ecs_cluster.dl_web_cluster.name} >> /etc/ecs/ecs.config;
                                       echo ECS_BACKEND_HOST= >> /etc/ecs/ecs.config;
                                       USERDATA

  vpc_classic_link_security_groups = []

  root_block_device {
    delete_on_termination = false
    encrypted             = false
    iops                  = 0
    throughput            = 0
    volume_size           = 30
    volume_type           = "gp2"
  }
}

resource "aws_autoscaling_group" "dl_web_asg" {
  capacity_rebalance        = false
  default_cooldown          = 300
  desired_capacity          = 2
  enabled_metrics           = []
  health_check_grace_period = 0
  health_check_type         = "EC2"
  launch_configuration      = aws_launch_configuration.ecs_launch_config.name
  load_balancers            = []
  max_instance_lifetime     = 0
  max_size                  = 2
  metrics_granularity       = "1Minute"
  min_size                  = 0
  name                      = "dl_web_asg"
  protect_from_scale_in     = false
  service_linked_role_arn   = "arn:aws:iam::955696714113:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"
  suspended_processes       = []
  target_group_arns         = []
  termination_policies      = []
  vpc_zone_identifier       = data.terraform_remote_state.base.outputs.public_subnet_ids

  timeouts {}
}
