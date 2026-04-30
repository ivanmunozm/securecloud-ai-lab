variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "github_repo" {
  description = "Repo de GitHub en formato usuario/repo"
  type        = string
}

variable "s3_bucket_name" {
  description = "Nombre del bucket de lab (debe ser globalmente único)"
  type        = string
}
