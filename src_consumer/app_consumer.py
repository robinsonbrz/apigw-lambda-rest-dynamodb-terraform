import logging
from controller import process_sqs_event


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if 'Records' in event:
        process_sqs_event(event)
