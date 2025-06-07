"""Configuration management for Listen-in."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.environ.get("OPEN_AI_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# Default paths
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "listen-in-output"
BASE_PATH = os.environ.get("LISTEN_IN_BASE_PATH", str(Path.cwd()))

# Default settings
DEFAULT_TONE = "conversational"
DEFAULT_AUDIENCE = "general"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
DEFAULT_QUALITY = "standard"
DEFAULT_DURATION = "default"

# Voice presets for podcast generation
PODCAST_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "domi": "AZnzlk1XvdvUeBnXmlld",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "adam": "pNInz6obpgDQGcFmaJgB",
    "charlie": "IKne3meq5aSn9XLyUdCD",
    "emily": "LcfcDJNUP1GQjkzn1xUU",
    "jessica": "cgSgspJ2msm6clMCkdW9",
    "matthew": "Yko7PKHZNXotIFUBG7I9"
}

# Model configuration
ELEVENLABS_MODEL_ID = "eleven_monolingual_v1"  # Good for English podcasts</ELEVENLABS_TURBO_MODEL = "eleven_turbo_v2_5"  # Faster generation