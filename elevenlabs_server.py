import os
from typing import Literal, Optional, Annotated
from pydantic import Field
from fastmcp import FastMCP, Context
from dotenv import load_dotenv
import httpx
import base64
import time
from pathlib import Path

# Load environment variables
load_dotenv()

# Create FastMCP server
mcp = FastMCP(
    name="ElevenLabs TTS Server",
    instructions="""
    This server provides text-to-speech capabilities using ElevenLabs API.
    Available tools:
    - list_voices: Get available voices
    - text_to_speech: Convert text to speech audio
    - get_voice_settings: Get default voice settings
    """
)

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Simple HTTP client for ElevenLabs
client = httpx.AsyncClient(
    base_url=ELEVENLABS_API_URL,
    headers={"xi-api-key": ELEVENLABS_API_KEY} if ELEVENLABS_API_KEY else {}
)

@mcp.tool
async def list_voices(ctx: Context) -> list[dict]:
    """List all available ElevenLabs voices with their details."""
    
    if not ELEVENLABS_API_KEY:
        await ctx.error("ElevenLabs API key not configured")
        return []
    
    try:
        await ctx.info("Fetching available voices from ElevenLabs")
        response = await client.get("/voices")
        response.raise_for_status()
        
        data = response.json()
        voices = data.get("voices", [])
        
        # Simplify voice data for LLM consumption
        simplified_voices = []
        for voice in voices:
            simplified_voices.append({
                "voice_id": voice["voice_id"],
                "name": voice["name"],
                "category": voice.get("category", "unknown"),
                "description": voice.get("description", ""),
                "preview_url": voice.get("preview_url", "")
            })
        
        await ctx.info(f"Found {len(simplified_voices)} voices")
        return simplified_voices
        
    except httpx.HTTPError as e:
        await ctx.error(f"Failed to fetch voices: {str(e)}")
        return []

@mcp.tool
async def text_to_speech(
    text: Annotated[str, Field(description="The text to convert to speech")],
    voice_id: Annotated[str, Field(description="Voice ID to use (get from list_voices)")] = "21m00Tcm4TlvDq8ikWAM",  # Default: Rachel
    output_directory: Annotated[Optional[str], Field(description="Directory to save the audio file. Defaults to Desktop.")] = None,
    model_id: Annotated[Literal["eleven_monolingual_v1", "eleven_multilingual_v2", "eleven_turbo_v2"], Field(description="Model to use")] = "eleven_monolingual_v1",
    stability: Annotated[float, Field(ge=0, le=1, description="Voice stability (0-1)")] = 0.5,
    similarity_boost: Annotated[float, Field(ge=0, le=1, description="Voice clarity/similarity boost (0-1)")] = 0.5,
    ctx: Context = None
) -> dict:
    """Convert text to speech using ElevenLabs API and save it to a file."""
    
    if not ELEVENLABS_API_KEY:
        return {"error": "ElevenLabs API key not configured"}
    
    if ctx:
        await ctx.info(f"Converting text to speech using voice {voice_id}")
        await ctx.debug(f"Text length: {len(text)} characters")
    
    try:
        # Prepare request data
        request_data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        # Make TTS request
        response = await client.post(
            f"/text-to-speech/{voice_id}",
            json=request_data
        )
        response.raise_for_status()
        
        # Get audio data
        audio_data = response.content
        
        if ctx:
            await ctx.info(f"Generated {len(audio_data)} bytes of audio")
        
        # Save audio to file
        if output_directory:
            output_path = Path(output_directory)
        else:
            output_path = Path.home() / "Desktop"
            
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(time.time())
        file_name = f"tts_{timestamp}.mp3"
        file_path = output_path / file_name
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
            
        if ctx:
            await ctx.info(f"Saved audio to {file_path}")

        return {
            "success": True,
            "file_path": str(file_path),
            "audio_size_bytes": len(audio_data),
            "format": "mp3",
            "text_length": len(text),
            "voice_id": voice_id,
            "model_id": model_id
        }
        
    except httpx.HTTPError as e:
        error_msg = f"Failed to generate speech: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {"error": error_msg}

@mcp.tool
async def get_voice_settings(
    voice_id: Annotated[str, Field(description="Voice ID to get settings for")]
) -> dict:
    """Get the default voice settings for a specific voice."""
    
    if not ELEVENLABS_API_KEY:
        return {"error": "ElevenLabs API key not configured"}
    
    try:
        response = await client.get(f"/voices/{voice_id}/settings")
        response.raise_for_status()
        
        return response.json()
        
    except httpx.HTTPError as e:
        return {"error": f"Failed to get voice settings: {str(e)}"}

@mcp.resource("resource://voices/list")
async def voices_resource() -> list[dict]:
    """Provides a list of available ElevenLabs voices as a resource."""
    # Create a minimal context for resource use
    # In production, you might want to handle this differently
    try:
        response = await client.get("/voices")
        response.raise_for_status()
        data = response.json()
        return data.get("voices", [])
    except:
        return []

@mcp.tool
async def check_api_status() -> dict:
    """Check if the ElevenLabs API is configured and accessible."""
    
    status = {
        "api_key_configured": bool(ELEVENLABS_API_KEY),
        "api_reachable": False,
        "api_url": ELEVENLABS_API_URL
    }
    
    if ELEVENLABS_API_KEY:
        try:
            # Try to fetch user info to verify API key
            response = await client.get("/user")
            response.raise_for_status()
            status["api_reachable"] = True
            status["user_info"] = response.json()
        except httpx.HTTPError as e:
            status["error"] = str(e)
    
    return status

# Cleanup on shutdown
async def cleanup():
    """Cleanup resources on server shutdown."""
    await client.aclose()

if __name__ == "__main__":
    import asyncio
    try:
        mcp.run()
    except KeyboardInterrupt:
        asyncio.run(cleanup()) 