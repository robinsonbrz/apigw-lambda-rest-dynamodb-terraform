import logging
from sqs.manager import process_sqs_message  # Assume you move SQS logic here
from api.controller import handle_api_gateway_event  # Updated import path

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if 'Records' in event:       # An SQS event
        return process_sqs_message(event)
    elif 'httpMethod' in event:  # An API Gateway event
        return handle_api_gateway_event(event)
