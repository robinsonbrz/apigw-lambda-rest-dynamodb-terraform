import logging

from api.controller import handle_api_gateway_event

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if 'httpMethod' in event:
        return handle_api_gateway_event(event)
