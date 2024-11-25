import logging
import boto3
import uuid
import json

class SqsManager:
    def __init__(self, queue_name):
        self.sqs = boto3.resource('sqs')
        self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)
        self.message_group="group1"

    def send_message(self, message, message_group=None, item=None):
        if item is not None:
            message_attributes = {
                key: {"StringValue": f"{item[key]}", "DataType": "String"}
                for key in item.keys()
            }
        else:
            message_attributes = {}

        message_deduplication_id=str(uuid.uuid4())
        if message_group is None:
            message_group=self.message_group

        response = self.queue.send_message(MessageBody=f'{message}',
            MessageGroupId=message_group, 
            MessageDeduplicationId=message_deduplication_id, 
            MessageAttributes=message_attributes
        )
        logging.info(f"Sqs message sent: {json.dumps(response)}")

        print(response.get('MessageId'))
        print(response.get('MD5OfMessageBody'))
        return response.get('MessageId')

def process_sqs_message(event):
    logging.info(f"Sqs Sqs Event received consumer: {json.dumps(event)}")
    for record in event.get("Records", []):
        logging.info(f"Sqs Sqs Record received consumer: {json.dumps(record)}")
