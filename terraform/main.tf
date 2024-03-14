terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.5.0" #version 3.5.0 or better
    }
  }
}

provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_budgets_budget" "WAFR-automation-suite" {
  name              = "monthly-budget"
  budget_type       = "COST"
  limit_amount      = "100.0"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2024-03-01_00:01"
}