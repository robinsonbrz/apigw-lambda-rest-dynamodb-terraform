import logging
from consumer_sqs import process_sqs_message
from api_controller import handle_api_gateway_event


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if 'Records' in event:       # An SQS event
        return process_sqs_message(event)
    elif 'httpMethod' in event:  # An API Gateway event
        return handle_api_gateway_event(event)
