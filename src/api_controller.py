import datetime
import boto3
import os
import json
import logging
import uuid
from send import SqsManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client('dynamodb')

def handle_api_gateway_event(event):
    table = os.environ.get('DDB_TABLE')
    http_method = event.get('httpMethod')
    logging.info(f"Event received api_controller.py: {json.dumps(event)}")


    if http_method == 'GET':
        path_parameters = event.get('pathParameters')
        movie_id = path_parameters.get('id') if path_parameters else None
        if movie_id:
            return get_movie_by_id(table, movie_id)
        else:
            return get_all_movies(table)

    elif http_method == 'POST':
        return create_movie(table, event)

    elif http_method == 'PUT':
        return update_movie(table, event)

    elif http_method == 'PATCH':
        return partially_update_movie(table, event)

    elif http_method == 'DELETE':
        return delete_movie(table, event)

    elif http_method == 'HEAD':
        return check_movie_exists(table, event)

    elif http_method == 'OPTIONS':
        return options_response()

    else:
        return {
            "statusCode": 405,  # Method Not Allowed
            "body": json.dumps({"error": "Method not supported"})
        }

def get_all_movies(table):
    try:
        response = dynamodb_client.scan(TableName=table)
        movies = response.get('Items', [])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(movies)
        }
    except Exception as e:
        logging.error(f"Error fetching movies: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch movies"})
        }

def get_movie_by_id(table, movie_id):
    try:
        response = dynamodb_client.get_item(
            TableName=table,
            Key={'id': {'S': movie_id}}
        )
        if 'Item' in response:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response['Item'])
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Movie not found"})
            }
    except Exception as e:
        logging.error(f"Error fetching movie by ID: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch movie"})
        }

def create_movie(table, event):
    logging.info(f"Loaded table name: {table}")
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
                "year": {'N': year},
                "title": {'S': title},
                "created_at": {'S': f'{created_at}'}
            }
        )
        four_digits =str(uuid.uuid4())[0:4]
        sqs = SqsManager('rob_fila_sqs.fifo')
        message_attributes={
            'year': {
                'StringValue': f'{year}',
                'DataType': 'String'
            },
            'title': {
                'StringValue': f'{title}',
                'DataType': 'String'
            },
            'created_at': {
                'StringValue': f'{created_at}',
                'DataType': 'String'
            },
            'movie_id': {
                'StringValue': f'{movie_id}',
                'DataType': 'String'
            }
        }

        sqs.send_message(f'Hello, {four_digits}', 'group1', message_attributes)

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Successfully inserted data!"})
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid input"})
        }

def update_movie(table, event):
    query_parameters = event.get('queryStringParameters')
    movie_id = query_parameters.get('movie_id') if query_parameters else None

    if not movie_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'movie_id' parameter in query string"})
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
                expression_attribute_values[f":{key}"] = {"N": str(value)}  # Ensure it is a number
            else:
                expression_attribute_values[f":{key}"] = {"S": str(value)} if isinstance(value, str) else {"N": str(value)}

        # Remove the trailing comma and space
        update_expression = update_expression[:-2]

        # Perform the update
        dynamodb_client.update_item(
            TableName=table,
            Key={'id': {'S': movie_id}},  # Ensure the key matches the type defined in your table
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Movie updated successfully"})
        }
    except Exception as e:
        logging.error(f"Error updating movie: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to update movie: {str(e)}"})
        }


def partially_update_movie(table, event):
    movie_id = event['pathParameters']['id']
    # query_parameters = event.get('queryStringParameters')
    # movie_id = query_parameters.get('movie_id') if query_parameters else None

    if not movie_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'movie_id' parameter in query string"})
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
                expression_attribute_values[f":{key}"] = {"N": str(value)}  # Convert string to number
            else:
                # For other fields, check type to decide if it's string or number
                expression_attribute_values[f":{key}"] = {"S": str(value)} if isinstance(value, str) else {"N": str(value)}

        # Remove the trailing comma and space
        update_expression = update_expression[:-2]

        # Perform the update
        dynamodb_client.update_item(
            TableName=table,
            Key={'id': {'S': movie_id}},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names  # Add this line
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Movie updated successfully"})
        }
    except Exception as e:
        logging.error(f"Error updating movie: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to update movie: {str(e)}"})
        }




def delete_movie(table, event):
    query_parameters = event.get('queryStringParameters')
    if query_parameters and 'movie_id' in query_parameters:
        movie_id = query_parameters['movie_id']
        dynamodb_client.delete_item(
            TableName=table,
            Key={'id': {'S': movie_id}}
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Movie with id {movie_id} deleted successfully, or nonexistent."})
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'id' parameter in query string"})
        }

def check_movie_exists(table, event):
    # Retrieve query parameters
    query_parameters = event.get('queryStringParameters')
    movie_id = query_parameters.get('movie_id') if query_parameters else None
    
    if not movie_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'movie_id' parameter in query"})
        }

    logging.info(f"Checking existence for movie_id: {movie_id}")

    try:
        response = dynamodb_client.get_item(
            TableName=table,
            Key={
                'id': {'S': movie_id}
            }
        )

        logging.info(f"Response from DynamoDB: {response}")

        # Check if the item exists
        if 'Item' in response:
            return {
                "statusCode": 200,
                "body": json.dumps({"exists": True})
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"exists": False})
            }
    
    except Exception as e:
        logging.error(f"Error checking movie existence: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to check existence: {str(e)}"})
        }

def options_response():
    return {
        "statusCode": 200,
        "headers": {
            "Allow": "GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS"
        },
        "body": json.dumps({"message": "Allowed methods: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS"})
    }
    
def generate_id():
    return str(uuid.uuid4())