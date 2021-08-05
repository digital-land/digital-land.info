output "ecr_repository" {
  value = data.aws_ecr_repository.dl_web_ecr.repository_url
}
