"""Simple audio generation using ElevenLabs text-to-speech API."""

import os
import aiohttp
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class SimpleAudioGenerator:
    """Simple generator for podcast audio using ElevenLabs TTS."""
    
    def __init__(self, api_key: str):
        """Initialize with ElevenLabs API key."""
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    async def generate_audio(
        self,
        script_content: str,
        output_path: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        model_id: str = "eleven_monolingual_v1",
        optimize_streaming_latency: int = 0,
        output_format: str = "mp3_44100_128"
    ) -> Dict[str, Any]:
        """
        Generate audio from a podcast script using ElevenLabs TTS.
        
        Args:
            script_content: The podcast script text
            output_path: Path to save the audio file
            voice_id: Voice ID to use
            model_id: Model ID for generation
            optimize_streaming_latency: Streaming optimization (0-4)
            output_format: Audio format
            
        Returns:
            Dictionary with audio file path and metadata
        """
        # Clean the script content (remove markdown formatting)
        clean_content = self._clean_script_content(script_content)
        
        # Prepare the request payload
        payload = {
            "text": clean_content,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        # Make the API request
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        params = {
            "optimize_streaming_latency": optimize_streaming_latency,
            "output_format": output_format
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"ElevenLabs API error: {response.status} - {error_text}")
                    
                    # Ensure directory exists
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write audio data
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    return {
                        "audio_path": output_path,
                        "voice_id": voice_id,
                        "model_id": model_id,
                        "status": "completed",
                        "generated_at": datetime.now().isoformat()
                    }
                        
            except Exception as e:
                raise RuntimeError(f"Failed to generate audio: {str(e)}")
    
    def _clean_script_content(self, script_content: str) -> str:
        """Clean script content for audio generation."""
        # Extract just the script portion (after "## Script" header)
        lines = script_content.split('\n')
        script_start = False
        clean_lines = []
        
        for line in lines:
            if line.strip() == "## Script":
                script_start = True
                continue
            elif line.strip().startswith("---") and script_start:
                break
            elif script_start and line.strip():
                # Skip markdown headers and metadata
                if not line.strip().startswith('#') and not line.strip().startswith('*'):
                    # Process special markers
                    cleaned = line.replace('[PAUSE]', '...')
                    cleaned = cleaned.replace('[EMPHASIS]', '')
                    clean_lines.append(cleaned)
        
        return ' '.join(clean_lines)
    
    async def get_voices(self) -> list[Dict[str, Any]]:
        """Get available voices from ElevenLabs."""
        headers = {"xi-api-key": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/voices",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise RuntimeError("Failed to fetch voices")
                
                data = await response.json()
                return data.get("voices", [])