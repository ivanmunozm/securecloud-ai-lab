variable "bucket_name" {
  description = "Nombre único del bucket (debe ser globalmente único en AWS)"
  type        = string
}

variable "environment" {
  description = "Entorno: lab, dev, staging, production"
  type        = string
  default     = "lab"
}
