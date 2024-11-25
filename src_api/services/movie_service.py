import datetime
import json
import uuid
import boto3
from sqs.manager import SqsManager

dynamodb_client = boto3.client("dynamodb")


class MovieService:
    def __init__(self, table_name):
        self.table_name = table_name

    def get_all_movies(self):
        try:
            response = dynamodb_client.scan(TableName=self.table_name)
            movies = response.get("Items", [])
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(movies),
            }
        except Exception as e:
            return self._handle_error(f"Failed to fetch movies: {str(e)}")

    def get_movie_by_id(self, movie_id):
        try:
            response = dynamodb_client.get_item(
                TableName=self.table_name, Key={"id": {"S": movie_id}}
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
            return self._handle_error(f"Failed to fetch movie: {str(e)}")

    def create_movie(self, item):
        try:
            year = str(item["year"])
            title = str(item["title"])
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            movie_id = str(uuid.uuid4())
            dynamodb_client.put_item(
                TableName=self.table_name,
                Item={
                    "id": {"S": movie_id},
                    "year": {"N": year},
                    "title": {"S": title},
                    "created_at": {"S": created_at},
                },
            )

            sqs = SqsManager("rob_fila_sqs.fifo")
            message_attributes = {
                "year": {"StringValue": year, "DataType": "String"},
                "title": {"StringValue": title, "DataType": "String"},
                "created_at": {"StringValue": created_at, "DataType": "String"},
                "movie_id": {"StringValue": movie_id, "DataType": "String"},
            }
            sqs.send_message(f"Movie Created: {title}", "group1", message_attributes)

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Successfully inserted data!"}),
            }
        except Exception as e:
            return self._handle_error(f"Failed to create movie: {str(e)}")

    @staticmethod
    def _handle_error(message):
        return {
            "statusCode": 500,
            "body": json.dumps({"error": message}),
        }
