# Myra AI Assistant

Myra is a private AI assistant built using Ollama, FastAPI, and Tailwind CSS. It provides a chat interface for users to interact with an AI model.

## Technologies Used

- Backend: FastAPI
- Frontend: HTML, JavaScript, Tailwind CSS
- AI Model: Ollama (llama2)

## Setup

1. Install dependencies:
   ```
   pip install fastapi uvicorn httpx python-dotenv loguru
   ```

2. Install Ollama and run the llama2 model:
   ```
   # Follow Ollama installation instructions from https://ollama.ai/
   ollama run llama2
   ```

3. Run the FastAPI server:
   ```
   uvicorn src.voice_assistant.app:app --reload
   ```

4. Open a web browser and navigate to `http://localhost:8000` to interact with Myra.

## Project Structure

- `src/voice_assistant/app.py`: FastAPI backend
- `static/index.html`: Frontend HTML and JavaScript
- `README.md`: This file

## Features

- Chat interface with AI-powered responses
- Error handling and loading states
- Responsive design using Tailwind CSS
- Integration with Ollama for AI model processing
- FastAPI backend for efficient API handling
- CORS middleware for cross-origin requests
- Health check endpoint for monitoring

## Usage

1. Type your message in the input field at the bottom of the page.
2. Press "Send" or hit Enter to send your message.
3. Myra will process your message and provide a response.
4. The conversation history is displayed in the chat window.

## Note

This is a development version and should not be used in production without proper security measures and optimizations.
