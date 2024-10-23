"""
FastAPI backend for Myra AI Assistant

This module implements a FastAPI application that serves as the backend for the Myra AI Assistant.
It handles chat interactions, serves static files, and provides health check endpoints.

The application uses Ollama for generating AI responses and streams these responses back to the client.
"""

import json
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()
stage = os.getenv("STAGE")

# Configure logger
if stage == "development":
    logger.remove()
    logger.add(sys.stderr, level="TRACE")

config_path = Path(__file__).parent / "core" / "logging" / "logging_config.json"

# Initialize FastAPI app
app = FastAPI(title="Myra AI Assistant", debug=stage == "development")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ChatMessage(BaseModel):
    """
    Pydantic model for chat messages.

    This model defines the structure of chat messages sent to and from the AI assistant.

    Attributes:
        message (str): The content of the chat message.
    """

    message: str = Field(..., description="The content of the chat message")

    @classmethod
    def __get_validators__(cls):
        """
        Get validators for the ChatMessage model.

        This method is used by Pydantic for model validation.

        Yields:
            callable: The validate method for this model.
        """
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """
        Validate the input for the ChatMessage model.

        This method allows the model to accept either a string or a dict with a 'message' key.

        Args:
            v: The value to validate.

        Returns:
            ChatMessage: A validated ChatMessage instance.

        Raises:
            ValueError: If the input is not a string or a dict with a 'message' key.
        """
        if isinstance(v, str):
            return cls(message=v)
        if isinstance(v, dict):
            return cls(**v)
        if isinstance(v, cls):
            return v
        error_message = "message must be a string or a dict with a 'message' key"
        raise ValueError(error_message)

    def __init__(self, **data):
        """
        Initialize a ChatMessage instance.

        This method ensures that the message attribute is a string.

        Args:
            **data: Keyword arguments to initialize the model.

        Raises:
            ValueError: If the message is not a string.
        """
        super().__init__(**data)
        if not isinstance(self.message, str):
            error_message = "message must be a string"
            raise ValueError(error_message)


@app.post("/chat")
async def chat(chat_message: ChatMessage) -> StreamingResponse:
    """
    Handle incoming chat messages and stream responses from Ollama.

    This endpoint receives a chat message, sends it to Ollama for processing,
    and streams the response back to the client.

    Args:
        chat_message (ChatMessage): The incoming chat message.

    Returns:
        StreamingResponse: A streaming response containing the AI's reply.

    Raises:
        HTTPException: If there's an error communicating with Ollama.
    """

    async def generate() -> AsyncGenerator[str, None]:
        """
        Generator function to stream the AI's response.

        This function handles the communication with Ollama and yields the response
        in chunks.

        Yields:
            str: Chunks of the AI's response in SSE format.
        """
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Received chat message: {chat_message.message}")
                async with client.stream(
                    "POST",
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": chat_message.message,
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    logger.debug(
                                        f"Yielding response chunk: {data['response']}"
                                    )
                                    yield f"data: {json.dumps(data)}\n\n"
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse JSON: {line}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            yield f"data: {json.dumps({'error': f'Error communicating with Ollama: {e!s}'})}\n\n"
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            yield f"data: {json.dumps({'error': f'Error connecting to Ollama: {e!s}'})}\n\n"
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            yield f"data: {json.dumps({'error': f'An unexpected error occurred: {e!s}'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/")
async def read_root() -> FileResponse:
    """
    Serve the index.html file.

    This endpoint serves the main HTML file for the chat interface.

    Returns:
        FileResponse: The index.html file.
    """
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health_check() -> dict:
    """
    Perform a health check on the API.

    This endpoint can be used to verify that the API is running and responsive.

    Returns:
        dict: A dictionary containing the status and a message.
    """
    return {"status": "healthy", "message": "Myra AI Assistant is running"}
