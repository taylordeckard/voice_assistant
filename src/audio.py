"""
Audio streaming and message handling for the Voice Assistant.

Provides functions to send microphone audio to OpenAI and play back audio responses.
"""

import asyncio
import base64
import json
import logging
from typing import Any

import numpy as np
import sounddevice as sd

from config import SAMPLE_RATE, CHUNK_SIZE, CHANNELS

logger = logging.getLogger(__name__)

output_stream: sd.OutputStream = sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype='int16',
)
output_stream.start()

async def receive_messages(websocket: Any) -> None:
    """
    Receive and process messages from the OpenAI WebSocket.

    Args:
        websocket (Any): The WebSocket connection to receive messages from.

    Returns:
        None
    """
    try:
        async for message in websocket:
            data: dict[str, Any] = json.loads(message)
            msg_type: str | None = data.get("type")

            if msg_type == "response.text.delta":
                print(data["text"], end="", flush=True)

            elif msg_type == "response.text":
                print()  # finalize assistant output line

            elif msg_type == "response.audio.delta":
                logger.debug("data keys: %s", list(data.keys()))
                audio_chunk: bytes = base64.b64decode(data["delta"])
                logger.debug("\U0001F50A Playing audio...")
                audio_np: np.ndarray = np.frombuffer(audio_chunk, dtype=np.int16)
                output_stream.write(audio_np)

            elif msg_type == "error":
                print(f"\n❌ ERROR: {data['error']['message']}")

            else:
                print(f"[Unhandled message type: {msg_type}]")
    except asyncio.CancelledError:
        logger.info("Message receiving cancelled.")
    finally:
        output_stream.close()

async def stream_audio(websocket: Any) -> None:
    """
    Record audio from the microphone in real-time and send it to OpenAI via WebSocket.

    Args:
        websocket (Any): The WebSocket connection to send audio data to.

    Returns:
        None
    """
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16',
        blocksize=CHUNK_SIZE,
    ) as stream:
        logger.info("🎙️ Start speaking...")
        try:
            while True:
                audio_chunk, _ = stream.read(CHUNK_SIZE)
                audio_bytes: bytes = audio_chunk.astype(np.int16).tobytes()
                encoded: str = base64.b64encode(audio_bytes).decode("utf-8")

                msg: dict[str, Any] = {
                    "type": "input_audio_buffer.append",
                    "audio": encoded
                }
                await websocket.send(json.dumps(msg))
                await asyncio.sleep(CHUNK_SIZE / SAMPLE_RATE)
        except asyncio.CancelledError:
            logger.info("🔇 Audio streaming stopped.")
