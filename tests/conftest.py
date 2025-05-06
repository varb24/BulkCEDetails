import os

import pytest
from lcg_common import load_env


@pytest.fixture
def client(monkeypatch, neo4j_client_fixture):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, ".env")
    load_env(env_path, required=True)

    # Import 'app' after monkeypatching
    from BulkCEDetailsAPI.server import app

    with app.test_client() as client:
        yield client
