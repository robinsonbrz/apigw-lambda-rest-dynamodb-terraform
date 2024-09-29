import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client('dynamodb')


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
            dynamodb_client.put_item(TableName=table,Item={"year": {'N':year}, "title": {'S':title}})
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
            dynamodb_client.put_item(TableName=table,Item={"year": {'N':'2012'}, "title": {'S':'The Amazing Spider-Man 2'}})
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": message})
            }
    else:
        return {
            "statusCode": 405,  # Method Not Allowed
            "body": json.dumps({"error": "Method not supported"})
        }