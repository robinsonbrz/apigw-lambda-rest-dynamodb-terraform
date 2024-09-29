import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client('dynamodb')


def generate_id():
    return str(uuid.uuid4())




def lambda_handler(event, context):
    table = os.environ.get('DDB_TABLE')
    http_method = event.get('httpMethod')
    
    if http_method == 'GET':
        print("\n\nGet method received\n\n")
        try:
            # Get all items from DynamoDB (you might need to adjust this if you have pagination)
            response = dynamodb_client.scan(TableName=table)
            movies = response.get('Items', [])  # Get items or an empty list if none found

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps(movies) 
            }
        except Exception as e:
            logging.error(f"Error fetching movies: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to fetch movies"})
            }
        
        
    elif http_method == 'POST':
        logging.info(f"## Loaded table name from environemt variable DDB_TABLE: {table}")
        if event["body"]:
            item = json.loads(event["body"])
            logging.info(f"## Received payload: {item}")
            year = str(item["year"])
            title = str(item["title"])
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "id": {"S": generate_id()},
                    "year": {'N': year},
                    "title": {'S': title}
                }
            )
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": message})
            }
        else:
            logging.info("## Received request without a payload")
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "S": generate_id(),
                    "year": {'N':'2012'}, 
                    "title": {'S':'The Amazing Spider-Man 2'}
                    }
            )
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": message})
            }
    elif http_method == 'DELETE':
        print("\n\nDelete method received\n\n")
        try:
            query_parameters = event.get('queryStringParameters')

            if query_parameters and 'id' in query_parameters:
                movie_id = query_parameters['id']
                dynamodb_client.delete_item(
                    TableName=table,
                    Key={
                        'id': {'S': movie_id}
                    }
                )
                
                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        {"message": f"Movie with id {movie_id} deleted successfully, or nonexistent."}
                    )
                }
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing 'id' parameter in query string"})
                }

        except Exception as e:
            logging.error(f"Error deleting movie: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Failed to delete movie: {str(e)}"})
            }

    else:
        return {
            "statusCode": 405,  # Method Not Allowed
            "body": json.dumps({"error": "Method not supported"})
        }