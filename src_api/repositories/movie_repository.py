import datetime
import json
import logging

from boto3 import client, resource


from api.utils import Utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = client("dynamodb")

dynamodb_resource = resource("dynamodb")




def get_movie_obj_by_id(table, movie_id):
    
    response = dynamodb_client.get_item(
            TableName=table, Key={"id": {"S": movie_id}}
        )

    movie = Utils.extract_item_values_from_dynamo_response(response)
    return movie