import json
import logging


def process_sqs_message(event):
    logging.info(f"Event received consummer: {json.dumps(event)}")
    for record in event.get("Records", []):
        logging.info(f"Record received consummer: {json.dumps(record)}")
        # print(f"Message ID: {record['messageId']}")
        # print(f"Message Body: {record['body']}")
    # return {"statusCode": 200, "body": json.dumps("SQS Message Processed")}
