terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = var.aws_region
}

resource "random_string" "random" {
  length  = 4
  special = false
}

resource "aws_dynamodb_table" "movie_table" {
  name           = var.dynamodb_table
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "id" # Only 'id' as the primary key

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "title"
    type = "S"
  }

  attribute {
    name = "year"
    type = "N"
  }

  global_secondary_index {
    name            = "TitleIndex"
    hash_key        = "title"
    projection_type = "ALL"
    read_capacity   = 10
    write_capacity  = 10
  }

  global_secondary_index {
    name            = "YearIndex"
    hash_key        = "year"
    projection_type = "ALL"
    read_capacity   = 10
    write_capacity  = 10
  }
}

#========================================================================
// sqs setup
#========================================================================


resource "aws_sqs_queue" "rob_fila_sqs" {
  name                       = "rob_fila_sqs.fifo"
  fifo_queue                 = true
  delay_seconds              = 0
  visibility_timeout_seconds = 30
  max_message_size           = 2048
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 2
  sqs_managed_sse_enabled    = true
}



#========================================================================
// lambda setup
#========================================================================

resource "aws_s3_bucket" "lambda_bucket" {
  bucket_prefix = var.s3_bucket_prefix
  force_destroy = true
}

# not allowed in Cloud Guru sandbox environment
# resource "aws_s3_bucket_acl" "private_bucket" {
#   bucket = aws_s3_bucket.lambda_bucket.id
#   acl    = "private"
# }

data "archive_file" "lambda_zip" {
  type = "zip"

  source_dir  = "${path.module}/src"
  output_path = "${path.module}/src.zip"
}

# Bucket that stores published lambda code
resource "aws_s3_object" "this" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "src.zip"
  source = data.archive_file.lambda_zip.output_path

  etag = filemd5(data.archive_file.lambda_zip.output_path)
}

//Define lambda function
resource "aws_lambda_function" "apigw_lambda_ddb" {
  function_name = "${var.lambda_name}-${random_string.random.id}"
  description   = "serverlessland pattern"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.this.key

  runtime = "python3.8"
  handler = "app.lambda_handler"

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  role = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      DDB_TABLE = var.dynamodb_table
    }
  }
  depends_on = [aws_cloudwatch_log_group.lambda_logs]

}

# CloudWatch
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name = "/aws/lambda/${var.lambda_name}-${random_string.random.id}"

  retention_in_days = var.lambda_log_retention
}

resource "aws_iam_role" "lambda_exec" {
  name = "LambdaDdbPost"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_exec_role" {
  name = "lambda-tf-pattern-ddb-post"

  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan"
        ],
        Resource = "arn:aws:dynamodb:*:*:table/${var.dynamodb_table}"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "sqs:GetQueueUrl",
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage"
        ],
        Resource = "arn:aws:sqs:*:*:rob_fila_sqs.fifo"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_exec_role.arn
}

#========================================================================
// API Gateway section
#========================================================================

resource "aws_apigatewayv2_api" "http_lambda" {
  name          = "${var.apigw_name}-${random_string.random.id}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.http_lambda.id

  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
  depends_on = [aws_cloudwatch_log_group.api_gw]
}

# If you want to catch POST individually use the commented code
# resource "aws_apigatewayv2_integration" "apigw_lambda" {
#   api_id = aws_apigatewayv2_api.http_lambda.id

#   integration_uri    = aws_lambda_function.apigw_lambda_ddb.invoke_arn
#   integration_type   = "AWS_PROXY"
#   integration_method = "POST"
# }

# resource "aws_apigatewayv2_route" "post" {
#   api_id = aws_apigatewayv2_api.http_lambda.id

#   route_key = "POST /movies"
#   target    = "integrations/${aws_apigatewayv2_integration.apigw_lambda.id}"
# }


resource "aws_apigatewayv2_integration" "apigw_lambda" {
  api_id           = aws_apigatewayv2_api.http_lambda.id
  integration_uri  = aws_lambda_function.apigw_lambda_ddb.invoke_arn
  integration_type = "AWS_PROXY"
}

# Use a wildcard route to catch all HTTP methods
resource "aws_apigatewayv2_route" "catch_all" {
  api_id    = aws_apigatewayv2_api.http_lambda.id
  route_key = "ANY /movies" # ANY matches all HTTP methods
  target    = "integrations/${aws_apigatewayv2_integration.apigw_lambda.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${var.apigw_name}-${random_string.random.id}"

  retention_in_days = var.apigw_log_retention
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.apigw_lambda_ddb.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.http_lambda.execution_arn}/*/*"
}


# # resource "aws_iam_role" "lambda_execution_role" {
# #   name               = "lambda_execution_role"
# #   assume_role_policy = jsonencode({
# #     Version = "2012-10-17"
# #     Statement = [
# #       {
# #         Action    = "sts:AssumeRole"
# #         Effect    = "Allow"
# #         Principal = {
# #           Service = "lambda.amazonaws.com"
# #         }
# #       }
# #     ]
# #   })
# # }

# # resource "aws_iam_policy" "lambda_sqs_policy" {
# #   name        = "lambda_sqs_policy"
# #   description = "Policy to allow Lambda to interact with SQS"

# #   policy = jsonencode({
# #     Version = "2012-10-17"
# #     Statement = [
# #       {
# #         Action = [
# #           "sqs:GetQueueUrl",
# #           "sqs:SendMessage",
# #           "sqs:ReceiveMessage",
# #           "sqs:DeleteMessage"
# #         ]
# #         Effect   = "Allow"
# #         Resource = "arn:aws:sqs:${var.region}:${data.aws_caller_identity.current.account_id}:rob_fila_sqs.fifo"
# #       }
# #     ]
# #   })
# # }

# # resource "aws_iam_role_policy_attachment" "lambda_sqs_policy_attachment" {
# #   role       = aws_iam_role.lambda_execution_role.name
# #   policy_arn = aws_iam_policy.lambda_sqs_policy.arn
# # }

# # resource "aws_lambda_function" "apigw_lambda_ddb" {
# #   function_name = "apigw_lambda_ddb"
# #   # Other Lambda function configurations...
# # }