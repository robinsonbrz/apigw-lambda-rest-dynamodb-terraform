import boto3
import uuid


class SqsManager:
    def __init__(self, queue_name):
        self.sqs = boto3.resource('sqs')
        self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)
        self.message_group="group1"

    def send_message(self, message, message_group=None, message_attributes=None):
        message_deduplication_id=str(uuid.uuid4())
        if message_group is None:
            message_group=self.message_group
        if message_attributes is None:
            message_attributes = {}

        response = self.queue.send_message(MessageBody=f'{message}',
            MessageGroupId=message_group, 
            MessageDeduplicationId=message_deduplication_id, 
            MessageAttributes=message_attributes
        )

        # The response is NOT a resource, but gives you a message ID and MD5
        print(response.get('MessageId'))
        print(response.get('MD5OfMessageBody'))
        return response.get('MessageId')
    