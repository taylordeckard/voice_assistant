# Voice Assistant

This project is a real-time voice assistant using OpenAI's GPT-4o model, audio streaming, and WebSockets.

## Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for fast Python package management and execution
- OpenAI API key (set in a `.env` file as `OPENAI_API_KEY`)

## Setup
Create a `.env` file in the project root with your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Program
To start the voice assistant (dependencies will be installed automatically):
```sh
uv run src/main.py
```

## Type Checking
To run type checks on the codebase:
```sh
uvx mypy src
```

## Notes
- Make sure your microphone and speakers are properly configured.
- The program uses `sounddevice` for audio I/O and `websockets` for communication.
