resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/api_gw/${var.apigw_name}-${random_string.random.id}"
  retention_in_days = var.apigw_log_retention
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}-${random_string.random.id}"
  retention_in_days = var.lambda_log_retention
}