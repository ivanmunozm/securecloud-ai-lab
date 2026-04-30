resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = {
    Lab     = "securecloud-ai"
    Purpose = "github-actions-oidc"
  }
}

resource "aws_iam_role" "github_actions_auditor" {
  name = "securecloud-ai-github-auditor"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
        }
      }
    }]
  })

  tags = {
    Lab = "securecloud-ai"
  }
}

resource "aws_iam_role_policy" "auditor_permissions" {
  name = "securecloud-ai-auditor-policy"
  role = aws_iam_role.github_actions_auditor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetBucketPolicy",
          "s3:GetBucketAcl",
          "s3:GetBucketVersioning",
          "s3:GetEncryptionConfiguration",
          "iam:GetRole",
          "iam:GetPolicy",
          "iam:ListRolePolicies",
          "iam:GetRolePolicy"
        ]
        Resource = "*"
      }
    ]
  })
}
