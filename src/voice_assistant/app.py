"""fast api hello world"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger

load_dotenv()
stage = os.getenv("STAGE")

if stage == "development":
    logger.remove()
    logger.add(sys.stderr, level="TRACE")

config_path = Path(__file__).parent / "core" / "logging" / "logging_config.json"

app = FastAPI(title="voice_assistant", debug=stage == "development")


@app.get("/")
def read_root():
    """
    The root endpoint, which logs various levels and returns a JSON response with a message and a pseudo-random number.

    Returns:
        dict
            A dictionary containing the message and pseudo-random number.
    """
    return {"message": "Hello, World!"}
