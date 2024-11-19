import json
import logging
import os

from api.handlers import (
    check_movie_exists,
    create_movie,
    delete_movie,
    get_all_movies,
    get_movie_by_id,
    partially_update_movie,
    update_movie,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_handler_mapping():
    return {
        "GET": handle_get,
        "POST": lambda event, table: create_movie(table, event),
        "PUT": lambda event, table: update_movie(table, event),
        "PATCH": lambda event, table: partially_update_movie(table, event),
        "DELETE": lambda event, table: delete_movie(table, event),
        "HEAD": lambda event, table: check_movie_exists(table, event),
    }


def handle_api_gateway_event(event):
    table = os.environ.get("DDB_TABLE")
    http_method = event.get("httpMethod")
    logger.info(f"Event received in controller.py: {event}")

    # Fetch the handler dynamically
    handler_mapping = get_handler_mapping()
    handler = handler_mapping.get(http_method, handle_not_supported)

    # Call the appropriate handler
    return handler(event, table)


def handle_get(event, table):
    if event.get("pathParameters") is not None:
        movie_id = event["pathParameters"]["id"]
        return get_movie_by_id(table, movie_id)
    return get_all_movies(table)


def handle_not_supported(event, table):
    return {
        "statusCode": 405,
        "body": json.dumps({"error": "Method not supported"}),
    }
