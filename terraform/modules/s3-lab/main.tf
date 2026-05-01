# ─────────────────────────────────────────────
# VERSIÓN VULNERABLE — para probar el auditor
# Tiene 3 problemas intencionales que el auditor
# debe detectar y bloquear el merge
# ─────────────────────────────────────────────

resource "aws_s3_bucket" "lab" {
  bucket = var.bucket_name

  tags = {
    Lab         = "securecloud-ai"
    Environment = var.environment
  }
}

# VULNERABILIDAD 1 (CRITICAL): acceso público habilitado
resource "aws_s3_bucket_public_access_block" "lab" {
  bucket = aws_s3_bucket.lab.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# VULNERABILIDAD 2 (HIGH): sin encryption at rest
# aws_s3_bucket_server_side_encryption_configuration no existe

# VULNERABILIDAD 3 (HIGH): sin versionamiento
# aws_s3_bucket_versioning no existe
# Test PR
