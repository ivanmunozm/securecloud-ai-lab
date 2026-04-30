output "github_actions_role_arn" {
  description = "Pegar este valor en GitHub Secrets como AWS_AUDIT_ROLE_ARN"
  value       = module.github_oidc.role_arn
}

output "oidc_provider_arn" {
  value = module.github_oidc.oidc_provider_arn
}
