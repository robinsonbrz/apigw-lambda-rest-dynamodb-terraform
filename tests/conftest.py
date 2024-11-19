# conftest.py
import pytest
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope="session")
def base_url():
    url=os.getenv("BASE_URL", "http://localhost")
    return f"{url}"

@pytest.fixture
def sget(base_url):
    # sget function to simplify GET requests
    def _sget(endpoint, params=None):
        return requests.get(f"{base_url}{endpoint}", params=params)
    return _sget

@pytest.fixture
def spost(base_url):
    # spost function to simplify POST requests
    def _spost(endpoint, data=None, json=None):
        return requests.post(f"{base_url}{endpoint}", data=data, json=json)
    return _spost
