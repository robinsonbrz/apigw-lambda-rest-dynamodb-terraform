import json
from typing import Dict, Optional

class StatusCodeHandler:
    @staticmethod
    def create_response(status_code: int, body: Optional[Dict] = None, message: Optional[str] = None) -> Dict:
        response = {
            "statusCode": status_code
        }

        response["headers"] = {"Content-Type": "application/json"}
        if body:
            response["body"] = json.dumps(body)

        elif message:
            response["body"] = json.dumps({"error": message})
            return response

        if status_code == 500:
            response["body"] = json.dumps({"error": "Internal Server Error"})
        elif status_code == 404:
            response["body"] = json.dumps({"error": "Not Found"})
        elif status_code == 400:
            response["body"] = json.dumps({"error": "Bad Request"})
        elif status_code == 401:
            response["body"] = json.dumps({"error": "Unauthorized"})
        elif status_code == 403:
            response["body"] = json.dumps({"error": "Forbidden"})


        return response