import uuid
import logging

class Utils:
    @staticmethod
    def generate_id():
        return str(uuid.uuid4())
    
    @staticmethod
    def extract_item_values_from_dynamo_response(item):
        item_valor = item.get("Item")
        resp = {}
        if item_valor is not None:
            for k, v in item_valor.items():
                logging.error(f"k,v: {k}, {v}")
                if v.get("S"):
                    resp[k]=v.get("S")
                elif v.get("N"):
                    resp[k]=v.get("N")
                elif v.get("B"):
                    resp[k]=v.get("B")
        return resp
