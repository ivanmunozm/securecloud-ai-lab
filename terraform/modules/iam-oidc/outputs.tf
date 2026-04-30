output "role_arn" {
  description = "ARN del rol que usará GitHub Actions"
  value       = aws_iam_role.github_actions_auditor.arn
}

output "oidc_provider_arn" {
  description = "ARN del OIDC provider creado"
  value       = aws_iam_openid_connect_provider.github.arn
}
