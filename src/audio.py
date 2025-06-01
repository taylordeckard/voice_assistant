import asyncio
import base64
import json
import numpy as np
import sounddevice as sd
from websockets.legacy.protocol import WebSocketCommonProtocol
from typing import Any

SAMPLE_RATE: int = 24000
CHUNK_SIZE: int = 1024
CHANNELS: int = 1

output_stream: sd.OutputStream = sd.OutputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype='int16',
)
output_stream.start()

async def receive_messages(websocket: WebSocketCommonProtocol) -> None:
    buffer: bytes = b''

    async for message in websocket:
        data: dict[str, Any] = json.loads(message)
        msg_type: str | None = data.get("type")

        if msg_type == "response.text.delta":
            print(data["text"], end="", flush=True)

        elif msg_type == "response.text":
            print()  # finalize assistant output line

        elif msg_type == "response.audio.delta":
            print(f"[DEBUG] data keys: {list(data.keys())}")
            audio_chunk: bytes = base64.b64decode(data["delta"])
            print("🔊 Playing audio...")
            audio_np: np.ndarray = np.frombuffer(audio_chunk, dtype=np.int16)
            output_stream.write(audio_np)

        elif msg_type == "error":
            print(f"\n❌ ERROR: {data['error']['message']}")

        else:
            print(f"[Unhandled message type: {msg_type}]")

async def stream_audio(websocket: WebSocketCommonProtocol) -> None:
    """Record audio in real-time and send to OpenAI via WebSocket"""
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16',
        blocksize=CHUNK_SIZE,
    ) as stream:
        print("🎙️ Start speaking...")
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
            print("🔇 Audio streaming stopped.")
            pass
