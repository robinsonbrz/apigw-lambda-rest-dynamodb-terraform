import logging

import os

from repositories.movie import MovieService


def process_sqs_event(event):
    table = os.environ.get("DDB_TABLE")
    movie_service = MovieService()
    records = event.get("Records")
    logging.info(f"consumer controller RECORDS: {records}")
    for record in records:
        logging.info(f"Sqs Attr Id: {record['messageAttributes']['id']['stringValue']}")
        movie_id = record["messageAttributes"]["id"]["stringValue"]
        item =movie_service.update_movie_by_id_set_approved_date(movie_id, table)
        logging.info(f"Item de mensagem: {item}")
