import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("BASE_URL", "http://localhost")
    return f"{url}"


@pytest.fixture
def first_movie_id(sget):
    response = sget("/movies")
    movies_list = response.json()
    if movies_list:
        return movies_list[0]["id"]["S"]  # Adjust based on your actual JSON structure
    return None


@pytest.fixture
def sget(base_url):
    def _sget(endpoint, params=None):
        return requests.get(f"{base_url}{endpoint}", params=params)

    return _sget


@pytest.fixture
def api_request(base_url):
    def _api_request(verb, endpoint, body=None, movie_id=None):
        url = f"{base_url}{endpoint}"
        if movie_id is not None:
            url = f"{url}/{movie_id}"

        verb = verb.lower()
        if verb == "post":
            return requests.post(url, json=body)
        elif verb == "patch":
            return requests.patch(url, json=body)
        elif verb == "put":
            return requests.put(url, json=body)
        elif verb == "delete":
            return requests.delete(url)
        elif verb == "head":
            return requests.head(url)
        else:
            raise ValueError(f"Unsupported HTTP verb: {verb}")

    return _api_request
