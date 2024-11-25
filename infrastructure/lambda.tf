resource "aws_s3_bucket" "lambda_bucket" {
  bucket_prefix = var.s3_bucket_prefix
  force_destroy = true
}

data "archive_file" "lambda_zip" {
  type = "zip"

  source_dir  = "../src_api"
  output_path = "${path.module}/src_api.zip"
}

resource "aws_s3_object" "this" {
  bucket = aws_s3_bucket.lambda_bucket.id
  key    = "src_api.zip"
  source = data.archive_file.lambda_zip.output_path

  etag = filemd5(data.archive_file.lambda_zip.output_path)
}

resource "aws_lambda_function" "apigw_lambda_ddb" {
  function_name = "${var.lambda_name}-api-${random_string.api_lambda_id.id}"
  description   = "Serverless Lambda function"

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

  depends_on = [aws_cloudwatch_log_group.api_lambda_logs]
}


# consumer Lambda function
data "archive_file" "lambda_zip_consumer" {
  type        = "zip"
  source_dir  = "../src_consumer"
  output_path = "${path.module}/src_consumer.zip"
}

resource "aws_s3_object" "consumer" {
  bucket = aws_s3_bucket.lambda_bucket.id
  key    = "src_consumer.zip"
  source = data.archive_file.lambda_zip_consumer.output_path
  etag   = filemd5(data.archive_file.lambda_zip_consumer.output_path)
}

resource "aws_lambda_function" "consumer_lambda" {
  function_name = "${var.lambda_name}-consumer-${random_string.consumer_lambda_id.id}"
  description   = "Consumer Lambda function"  

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_object.consumer.key

  runtime = "python3.8"
  handler = "app_consumer.lambda_handler"

  source_code_hash = data.archive_file.lambda_zip_consumer.output_base64sha256

  role = aws_iam_role.lambda_exec.arn


  environment {
    variables = {
      DDB_TABLE = var.dynamodb_table
    }
  }
    depends_on = [aws_cloudwatch_log_group.consumer_lambda_logs]
}