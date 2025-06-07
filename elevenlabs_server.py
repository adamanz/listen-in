import os
from typing import Literal, Optional, Annotated
from pydantic import Field
from fastmcp import FastMCP, Context
from dotenv import load_dotenv
import httpx
import base64
import time
from pathlib import Path
import asyncio
from aiohttp import web
import json
import logging

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
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))

# Simple HTTP client for ElevenLabs
client = httpx.AsyncClient(
    base_url=ELEVENLABS_API_URL,
    headers={"xi-api-key": ELEVENLABS_API_KEY} if ELEVENLABS_API_KEY else {}
)

# Core functions for both MCP and HTTP
async def _list_voices(ctx=None) -> list[dict]:
    """List all available ElevenLabs voices with their details."""
    
    if not ELEVENLABS_API_KEY:
        if ctx:
            await ctx.error("ElevenLabs API key not configured")
        return []
    
    try:
        if ctx:
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
        
        if ctx:
            await ctx.info(f"Found {len(simplified_voices)} voices")
        return simplified_voices
        
    except httpx.HTTPError as e:
        if ctx:
            await ctx.error(f"Failed to fetch voices: {str(e)}")
        return []

@mcp.tool
async def list_voices(ctx: Context) -> list[dict]:
    """List all available ElevenLabs voices with their details."""
    return await _list_voices(ctx)

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



# HTTP Server for payment gateway integration
async def handle_call(request):
    """Handle JSON-RPC style calls from the payment gateway"""
    try:
        data = await request.json()
        method = data.get("method", "")
        params = data.get("params", {})
        
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in ["list_voices", "text_to_speech", "get_voice_settings", "check_api_status"]:
                return web.json_response({
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }, status=404)
            
            # Create a minimal context for HTTP calls
            class MinimalContext:
                async def info(self, msg): 
                    logging.info(msg)
                async def error(self, msg): 
                    logging.error(msg)
                async def debug(self, msg): 
                    logging.debug(msg)
            
            # Call the tool function directly
            try:
                if tool_name == "list_voices":
                    result = await _list_voices(MinimalContext())
                elif tool_name == "text_to_speech":
                    # Call text_to_speech without the decorator
                    if not ELEVENLABS_API_KEY:
                        result = {"error": "ElevenLabs API key not configured"}
                    else:
                        # Extract arguments with defaults
                        text = arguments.get("text", "")
                        voice_id = arguments.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
                        logging.info(f"Text to speech request - text: '{text}', arguments: {arguments}")
                        output_directory = arguments.get("output_directory", None)
                        model_id = arguments.get("model_id", "eleven_monolingual_v1")
                        stability = arguments.get("stability", 0.5)
                        similarity_boost = arguments.get("similarity_boost", 0.5)
                        
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
                        
                        result = {
                            "success": True,
                            "file_path": str(file_path),
                            "audio_size_bytes": len(audio_data),
                            "format": "mp3",
                            "text_length": len(text),
                            "voice_id": voice_id,
                            "model_id": model_id
                        }
                elif tool_name == "get_voice_settings":
                    voice_id = arguments.get("voice_id")
                    if not ELEVENLABS_API_KEY:
                        result = {"error": "ElevenLabs API key not configured"}
                    else:
                        response = await client.get(f"/voices/{voice_id}/settings")
                        response.raise_for_status()
                        result = response.json()
                elif tool_name == "check_api_status":
                    result = {
                        "api_key_configured": bool(ELEVENLABS_API_KEY),
                        "api_reachable": False,
                        "api_url": ELEVENLABS_API_URL
                    }
                    
                    if ELEVENLABS_API_KEY:
                        try:
                            response = await client.get("/user")
                            response.raise_for_status()
                            result["api_reachable"] = True
                            result["user_info"] = response.json()
                        except httpx.HTTPError as e:
                            result["error"] = str(e)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
            except Exception as e:
                logging.exception(f"Error calling tool {tool_name}")
                result = {"error": str(e)}
            
            return web.json_response({
                "result": result
            })
        else:
            return web.json_response({
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }, status=404)
            
    except Exception as e:
        logging.exception("Error handling request")
        return web.json_response({
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status=500)

async def create_app():
    """Create the aiohttp application"""
    app = web.Application()
    app.router.add_post('/call', handle_call)
    return app

# Cleanup on shutdown
async def cleanup():
    """Cleanup resources on server shutdown."""
    await client.aclose()

# HTTP server runner
async def run_http_server():
    """Run the HTTP server"""
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', HTTP_PORT)
    await site.start()
    print(f"HTTP server running on http://localhost:{HTTP_PORT}")
    
    # Keep the server running
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    import sys
    
    # Check if we should run as HTTP server or MCP server
    if "--http" in sys.argv:
        # Run as HTTP server
        print("Starting ElevenLabs HTTP server...")
        try:
            asyncio.run(run_http_server())
        except KeyboardInterrupt:
            print("\nShutting down HTTP server...")
            asyncio.run(cleanup())
    else:
        # Run as MCP server (default)
        try:
            mcp.run()
        except KeyboardInterrupt:
            asyncio.run(cleanup()) 