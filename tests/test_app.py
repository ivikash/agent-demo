import os
import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from src.voice_assistant.app import app


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)


def test_read_root(test_client):
    # Simulate environment variables
    with patch.dict(os.environ, {"STAGE": "test"}):
        # Send a GET request to the root endpoint
        response = test_client.get("/")

        # Ensure the request was successful
        assert response.status_code == 200

        message = response.json().get("message", "")
        assert re.match(
            r"Hello, World!", message
        ), f"Expected message to match pattern, but got: {message}"

        log_content = response.content.decode()
        assert "Hello, World!" in log_content
