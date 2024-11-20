import datetime
import json
import logging
import uuid

from boto3 import client

from api.utils import generate_id
from sqs.manager import SqsManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = client("dynamodb")


def get_all_movies(table):
    try:
        response = dynamodb_client.scan(TableName=table)
        movies = response.get("Items", [])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(movies),
        }
    except Exception as e:
        logging.error(f"Error fetching movies: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch movies"}),
        }


def get_movie_by_id(table, movie_id):
    try:
        response = dynamodb_client.get_item(
            TableName=table, Key={"id": {"S": movie_id}}
        )
        if "Item" in response:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response["Item"]),
            }
        else:
            return {"statusCode": 404, "body": json.dumps({"error": "Movie not found"})}
    except Exception as e:
        logging.error(f"Error fetching movie by ID: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch movie"}),
        }


def create_movie(table, event):
    if event["body"]:
        item = json.loads(event["body"])
        year = str(item["year"])
        title = str(item["title"])
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        movie_id = generate_id()
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "id": {"S": movie_id},
                "year": {"N": year},
                "title": {"S": title},
                "created_at": {"S": f"{created_at}"},
            },
        )
        four_digits = str(uuid.uuid4())[0:4]
        sqs = SqsManager("rob_fila_sqs.fifo")
        message_attributes = {
            "movie_id": {"StringValue": f"{movie_id}", "DataType": "String"},
            "year": {"StringValue": f"{year}", "DataType": "String"},
            "title": {"StringValue": f"{title}", "DataType": "String"},
            "created_at": {"StringValue": f"{created_at}", "DataType": "String"},
        }

        sqs.send_message(f"Hello, {four_digits}", "group1", message_attributes)

        resp_body={
            "id": movie_id,
            "year": year,
            "title": title,
            "created_at": created_at
        }
        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(resp_body),
        }
    else:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid input"})}


def update_movie(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
    else:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Missing 'movie_id' parameter in path string"}
            ),
        }

    try:
        # Get the update fields from the request body
        update_fields = json.loads(event.get("body", "{}"))

        # Construct the update expression
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in update_fields.items():
            # Handle reserved keywords (like 'year')
            expression_attribute_names[f"#{key}"] = key

            update_expression += f"#{key} = :{key}, "

            if key == "year":
                expression_attribute_values[f":{key}"] = {
                    "N": str(value)
                }  # Ensure it is a number
            else:
                expression_attribute_values[f":{key}"] = (
                    {"S": str(value)} if isinstance(value, str) else {"N": str(value)}
                )

        # Remove the trailing comma and space
        update_expression = update_expression[:-2]

        # Perform the update
        dynamodb_client.update_item(
            TableName=table,
            Key={
                "id": {"S": movie_id}
            },  # Ensure the key matches the type defined in your table
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Movie updated successfully"}),
        }
    except Exception as e:
        logging.error(f"Error updating movie: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to update movie: {str(e)}"}),
        }


def partially_update_movie(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
    else:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Missing 'movie_id' parameter in path string"}
            ),
        }

    try:
        # Get the update fields from the request body
        update_fields = json.loads(event.get("body", "{}"))

        # Construct the update expression
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in update_fields.items():
            # Use a placeholder for reserved keywords
            expression_attribute_names[f"#{key}"] = key

            update_expression += f"#{key} = :{key}, "

            if key == "year":
                # Ensure 'year' is treated as a number for the update
                expression_attribute_values[f":{key}"] = {
                    "N": str(value)
                }  # Convert string to number
            else:
                # For other fields, check type to decide if it's string or number
                expression_attribute_values[f":{key}"] = (
                    {"S": str(value)} if isinstance(value, str) else {"N": str(value)}
                )

        # Remove the trailing comma and space
        update_expression = update_expression[:-2]

        # Perform the update
        dynamodb_client.update_item(
            TableName=table,
            Key={"id": {"S": movie_id}},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,  # Add this line
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Movie updated successfully"}),
        }
    except Exception as e:
        logging.error(f"Error updating movie: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to update movie: {str(e)}"}),
        }


def delete_movie(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
        dynamodb_client.delete_item(TableName=table, Key={"id": {"S": movie_id}})
        return {
            "statusCode": 204,
            "body": json.dumps(
                {
                    "message": f"Movie with id {movie_id} deleted successfully, or nonexistent."
                }
            ),
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'id' parameter in query string"}),
        }


def check_movie_exists(table, event):
    # Retrieve query parameters
    logging.info(f"HEAD Event received api_controller.py: {json.dumps(event)}")

    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'movie_id' parameter in query"}),
        }

    logging.info(f"Checking existence for movie_id: {movie_id}")

    try:
        response = dynamodb_client.get_item(
            TableName=table, Key={"id": {"S": movie_id}}
        )

        logging.info(f"Response from DynamoDB: {response}")

        # Check if the item exists
        if "Item" in response:
            return {"statusCode": 200, "body": json.dumps({"exists": True})}
        else:
            return {"statusCode": 404, "body": json.dumps({"exists": False})}

    except Exception as e:
        logging.error(f"Error checking movie existence: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to check existence: {str(e)}"}),
        }
