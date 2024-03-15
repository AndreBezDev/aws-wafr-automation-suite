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
