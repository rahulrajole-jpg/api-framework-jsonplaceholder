import pytest
from db.sqlite_client import SQLiteClient
from src.api.base_client import BaseClient
import yaml

@pytest.fixture(scope="session")
def config():
    with open("config/config.yaml") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def db():
    return SQLiteClient()

@pytest.fixture(scope="session")
def base_url(config):
    return config["base_url"]

@pytest.fixture(scope="session")
def api_client(base_url):
    return BaseClient(base_url)
