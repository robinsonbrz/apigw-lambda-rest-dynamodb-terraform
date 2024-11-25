import logging
import boto3
import datetime

dynamodb_client = boto3.client("dynamodb")

class MovieService:
    def __init__(self):
        pass

    def get_movie_by_id(self, movie_id, table_name):

        response = dynamodb_client.get_item(
            TableName=table_name, Key={"id": {"S": movie_id}}
        )
        if "Item" in response:
            return response["Item"]
        else:
            return None


    def update_movie_by_id_set_approved_date(self, movie_id, table_name):
        logging.info(f"movie_id: {movie_id}")
        logging.info(f"table_name: {table_name}")
        try:
            approved_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            response = dynamodb_client.update_item(
                TableName=table_name,
                Key={"id": {"S": movie_id}},
                UpdateExpression="SET approved_date = :date",
                ExpressionAttributeValues={
                    ":date": {"S": approved_date}
                },
                ReturnValues="UPDATED_NEW"
            )
            logging.info(f"Response apos escrita: {response}")
            return response
        except dynamodb_client.exceptions.ConditionalCheckFailedException:
            logging.info("Erro exceção na escrita")
            return {"error": "Condition failed. Update not applied."}
        except Exception as e:
            logging.info(f"Erro {e}")
            return {"error": str(e)}
