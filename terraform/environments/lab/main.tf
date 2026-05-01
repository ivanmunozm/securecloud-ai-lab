terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
}

module "github_oidc" {
  source = "../../modules/iam-oidc"

  github_repo    = var.github_repo
  tfstate_bucket = ""
}

module "s3_lab" {
  source = "../../modules/s3-lab"

  bucket_name = var.s3_bucket_name
  environment = "lab"
}
