terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.5.0" #version 3.5.0 or better
    }
  }
}

# Default provider
provider "aws" {
  region = "ap-southeast-2"
}

# Secondary region via alias
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"  # Specify the AWS region for the CloudWatch Logs group
}

# Create monthly budget
resource "aws_budgets_budget" "WAFR-automation-suite" {
  name              = "monthly-budget"
  budget_type       = "COST"
  limit_amount      = "100.0"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2024-03-01_00:01"
}

#create ECR repo # To Do - implement image scanning
resource "aws_ecr_repository" "WAFR-Bot-Images" {
  provider = aws.us_east_1
  name = "wafr-bot-images"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

# # Create Lambda with Container Image

# resource "aws_lambda_function" "WAFR-LangChain-Lambda" {
#   provider         = aws.us_east_1
#   function_name    = "WAFR-AI-BOT-lambda"
#   role             = aws_iam_role.lambda_exec_role_wafr_bot.arn
#   runtime = "python3.11"
#   handler = "main.handler"
#   timeout          = 360
#   memory_size      = 2048
#   publish          = true
#   package_type     = "Image"
#   image_uri        = "720050647263.dkr.ecr.us-east-1.amazonaws.com/wafr-bot-images:latest"
# }

# resource "aws_iam_role" "lambda_exec_role_wafr_bot" {
#   name = "lambda-exec-role-wafr-bot"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect    = "Allow"
#       Principal = {
#         Service = "lambda.amazonaws.com"
#       }
#       Action    = "sts:AssumeRole"
#     }]
#   })
# }

resource "aws_iam_policy" "lambda_exec_policy_wafr_bot" {
  name        = "lambda-exec-policy-wafr-bot"
  description = "Policy for Lambda execution role wafr bot"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = [
          "bedrock:*"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attachment_wafr_bot" {
#   role       = aws_iam_role.lambda_exec_role_wafr_bot.name
#   policy_arn = aws_iam_policy.lambda_exec_policy_wafr_bot.arn
# }


# Create Bedrock Invocations CW Log Group
resource "aws_cloudwatch_log_group" "bedrock_invocation_logs" {
  provider          = aws.us_east_1  # Use the provider for us-east-1 region
  name              = "/bedrock/invocation-logs"  # Specify the name of the log group
  retention_in_days = 7  # Specify the retention period for logs (in days)
}

# Create S3 buckets
resource "aws_s3_bucket" "templates_bucket" {
  bucket = "aws-wafr-automation-base-templates"
  acl    = "private"
}

resource "aws_s3_bucket" "input_wafr_reports_bucket" {
  bucket = "aws-wafr-automation-input-reports"
  acl    = "private"
}

resource "aws_s3_bucket" "output_reports_bucket" {
  bucket = "aws-wafr-automation-output-reports"
  acl    = "private"

  # Enable versioning
  versioning {
    enabled = true
  }

  # Configure server-side encryption
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
