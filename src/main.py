"""
Main entry point for the Voice Assistant.

Handles connection to OpenAI's GPT-4o real-time API and coordinates audio
streaming and message handling.
"""

import asyncio
import json
import logging
from typing import Any

from websockets.asyncio.client import connect

from config import OPENAI_API_KEY
from audio import receive_messages, stream_audio

async def main() -> None:
    """
    Connect to the OpenAI GPT-4o real-time WebSocket API, start a session,
    and concurrently stream audio and receive messages.

    Returns:
        None
    """
    logging.basicConfig(level=logging.INFO)

    uri: str = (
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    )
    headers: dict[str, str] = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    async with connect(uri, additional_headers=headers) as websocket:  # type: ignore
        # Start session
        await websocket.send(json.dumps({
            "type": "session.update",
            "session": {
                "model": "gpt-4o",
                "instructions": "Respond quickly and concisely.",
            }
        }))

        # Run audio and message handling concurrently
        await asyncio.gather(
            stream_audio(websocket),
            receive_messages(websocket),
        )

if __name__ == "__main__":
    asyncio.run(main())
