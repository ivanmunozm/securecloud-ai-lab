variable "github_repo" {
  description = "Repo de GitHub en formato usuario/repo"
  type        = string
}

variable "tfstate_bucket" {
  description = "Nombre del bucket S3 para el terraform state"
  type        = string
  default     = ""
}