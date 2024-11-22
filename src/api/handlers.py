import datetime
import json
import logging

from boto3 import client, resource

from api.utils import Utils
from sqs.manager import SqsManager
from status_codes.status_codes import StatusCodeHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = client("dynamodb")

dynamodb_resource = resource("dynamodb")


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
        return StatusCodeHandler.create_response(500)

def get_movie_by_id(table, movie_id):
    try:
        response = dynamodb_client.get_item(
            TableName=table, Key={"id": {"S": movie_id}}
        )

        body = Utils.extract_item_values_from_dynamo_response(response)

        if body != {}:
            return StatusCodeHandler.create_response(200, body=body)
        else:
            return StatusCodeHandler.create_response(404)
    except Exception:
        return StatusCodeHandler.create_response(500)


def create_movie(table, event):
    table = dynamodb_resource.Table(table)

    if event["body"]:
        item = json.loads(event["body"])
        item_body = {
            "id": Utils.generate_id(),
            "year": item["year"],
            "title": item["title"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        table.put_item(
            Item=item_body,
        )
        sqs = SqsManager("rob_fila_sqs.fifo")
        sqs.send_message(f"Hello, {item_body['id']}", "group1", item_body)

        return StatusCodeHandler.create_response(201, body=item_body)

    else:
        return StatusCodeHandler.create_response(400, "Missing body to create register")


def update_movie(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
    else:
        return StatusCodeHandler.create_response(
            400, "Missing 'movie_id' parameter in path string"
        )

    try:
        update_fields = json.loads(event.get("body", "{}"))
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
        return StatusCodeHandler.create_response(500)


def partially_update_movie(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
    else:
        return StatusCodeHandler.create_response(
            400, "Missing 'movie_id' parameter in path string"
        )

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
            ExpressionAttributeNames=expression_attribute_names,
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Movie updated successfully"}),
        }
    except Exception as e:
        logging.error(f"Error updating movie: {str(e)}")
        return StatusCodeHandler.create_response(500)


def delete_movie(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
        dynamodb_client.delete_item(TableName=table, Key={"id": {"S": movie_id}})
        return StatusCodeHandler.create_response(204)
    else:
        return StatusCodeHandler.create_response(400)


def check_movie_exists(table, event):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
    else:
        return StatusCodeHandler.create_response(400)

    logging.info(f"Checking existence for movie_id: {movie_id}")

    try:
        response = dynamodb_client.get_item(
            TableName=table, Key={"id": {"S": movie_id}}
        )

        if "Item" in response:
            return StatusCodeHandler.create_response(200, {"exists": True})
        else:
            return StatusCodeHandler.create_response(404, {"exists": False})

    except Exception as e:
        logging.error(f"Error checking movie existence: {str(e)}")

        return StatusCodeHandler.create_response(500)
