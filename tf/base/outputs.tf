output "dns_domain_validation_options" {
  value = aws_acm_certificate.dl_web_acm_certificate.domain_validation_options
}

output "vpc_id" {
  value = aws_vpc.dl_web_vpc.id
}

output "public_subnet_ids" {
  value = aws_subnet.public.*.id
}

output "load_balancer_arn" {
  value = aws_lb.dl_web_lb.arn
}

output "ecs_instance_sg_id" {
  value = aws_security_group.ecs_instance_sg.id
}

output "certificate_arn" {
  value = aws_acm_certificate.dl_web_acm_certificate.arn
}
