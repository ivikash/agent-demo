from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from src.voice_assistant import ChatMessage, app


@pytest.fixture()
async def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_post = AsyncMock()
        mock_instance.post.return_value = mock_post
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio()
async def test_chat_endpoint_success(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.aiter_lines.return_value = [
        '{"response": "Hello", "done": false}',
        '{"response": " world", "done": false}',
        '{"response": "!", "done": true}',
    ]
    mock_httpx_client.return_value.__aenter__.return_value.post.return_value = (
        mock_response
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/chat", json={"message": "Hi there"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    content = response.content.decode()
    assert 'data: {"response": "Hello"' in content
    assert 'data: {"response": " world"' in content
    assert 'data: {"response": "!"' in content


@pytest.mark.asyncio()
async def test_chat_endpoint_invalid_input():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/chat", json={"message": 123}
        )  # Invalid input: number instead of string

    assert response.status_code == 422  # Unprocessable Entity
    assert "message" in response.json()["detail"][0]["loc"]


def test_chat_message():
    message = "Hello, world!"
    chat_message = ChatMessage(message=message)
    assert chat_message.message == message

    with pytest.raises(ValueError, match="Input should be a valid string"):
        ChatMessage(message=123)  # Should raise an error for non-string input


@pytest.mark.asyncio()
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/health")

    assert response.status_code == 200


@pytest.mark.asyncio()
async def test_read_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
