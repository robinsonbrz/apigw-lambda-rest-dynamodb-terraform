resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/api_gw/${var.apigw_name}-${random_string.random.id}"
  retention_in_days = var.apigw_log_retention
}

resource "aws_cloudwatch_log_group" "api_lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}-api-${random_string.api_lambda_id.id}"
  retention_in_days = var.lambda_log_retention
}

resource "aws_cloudwatch_log_group" "consumer_lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}-consumer-${random_string.consumer_lambda_id.id}"
  retention_in_days = var.lambda_log_retention
}
