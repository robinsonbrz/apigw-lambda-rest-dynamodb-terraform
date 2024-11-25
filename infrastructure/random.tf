resource "random_string" "random" {
  length  = 4
  special = false
}

resource "random_string" "api_lambda_id" {
  length  = 6
  special = false
  upper   = false
}

resource "random_string" "consumer_lambda_id" {
  length  = 6
  special = false
  upper   = false
}