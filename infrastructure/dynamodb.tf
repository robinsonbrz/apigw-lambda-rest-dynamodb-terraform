resource "aws_dynamodb_table" "movie_table" {
  name           = var.dynamodb_table
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "id"

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
