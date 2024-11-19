output "apigwy_url" {
  description = "URL for API Gateway stage"
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "lambda_log_group" {
  description = "Name of the CloudWatch logs group for the Lambda function"
  value       = aws_cloudwatch_log_group.lambda_logs.id
}

output "apigwy_log_group" {
  description = "Name of the CloudWatch logs group for the API Gateway"
  value       = aws_cloudwatch_log_group.api_gw.id
}

output "queue_url" {
  value = aws_sqs_queue.rob_fila_sqs.url
}
