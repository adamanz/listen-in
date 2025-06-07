"""Audio generation using ElevenLabs API."""

import os
import json
import aiohttp
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class AudioGenerator:
    """Generator for podcast audio using ElevenLabs."""
    
    def __init__(self, api_key: str):
        """Initialize with ElevenLabs API key."""
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    async def generate_audio(
        self,
        script_content: str,
        output_path: str,
        voice_mode: str = "bulletin",
        quality: str = "standard",
        duration_scale: str = "default",
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio from a podcast script using ElevenLabs.
        
        Args:
            script_content: The podcast script text
            output_path: Path to save the audio file
            voice_mode: "bulletin" for monologue, "conversation" for dialogue
            quality: Audio quality preset
            duration_scale: Length preference (short/default/long)
            voice_id: Specific voice to use
            model_id: Model ID for generation
            callback_url: Optional webhook for async processing
            
        Returns:
            Dictionary with audio file path and metadata
        """
        # Get default model if not specified
        if not model_id:
            model_id = await self._get_default_model()
        
        # Prepare the request payload
        payload = {
            "model_id": model_id,
            "mode": {
                "type": voice_mode
            },
            "source": {
                "type": "text",
                "text": script_content
            },
            "quality_preset": quality,
            "duration_scale": duration_scale,
            "language": "en"  # Default to English
        }
        
        # Add callback URL if provided
        if callback_url:
            payload["callback_url"] = callback_url
        
        # Add voice configuration for bulletin mode
        if voice_mode == "bulletin" and voice_id:
            payload["mode"]["voice_id"] = voice_id
        
        # Make the API request
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/projects/add",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"ElevenLabs API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    project_id = result["project"]["project_id"]
                    
                    # If no callback, wait for completion
                    if not callback_url:
                        audio_url = await self._wait_for_completion(session, project_id, headers)
                        
                        # Download the audio file
                        await self._download_audio(session, audio_url, output_path)
                        
                        return {
                            "audio_path": output_path,
                            "project_id": project_id,
                            "status": "completed",
                            "quality": quality,
                            "duration_scale": duration_scale,
                            "generated_at": datetime.now().isoformat()
                        }
                    else:
                        # Return project info for async processing
                        return {
                            "project_id": project_id,
                            "status": "processing",
                            "callback_url": callback_url,
                            "quality": quality,
                            "duration_scale": duration_scale,
                            "submitted_at": datetime.now().isoformat()
                        }
                        
            except Exception as e:
                raise RuntimeError(f"Failed to generate audio: {str(e)}")
    
    async def _get_default_model(self) -> str:
        """Get the default podcast model from ElevenLabs."""
        headers = {"xi-api-key": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/models",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise RuntimeError("Failed to fetch models")
                
                models = await response.json()
                # Look for a podcast-optimized model
                for model in models:
                    if "podcast" in model.get("name", "").lower():
                        return model["model_id"]
                
                # Fallback to first available model
                if models:
                    return models[0]["model_id"]
                
                raise RuntimeError("No models available")
    
    async def _wait_for_completion(
        self, 
        session: aiohttp.ClientSession, 
        project_id: str, 
        headers: Dict[str, str],
        max_attempts: int = 60,
        delay_seconds: int = 5
    ) -> str:
        """Poll for project completion and return audio URL."""
        import asyncio
        
        for _ in range(max_attempts):
            async with session.get(
                f"{self.base_url}/projects/{project_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    raise RuntimeError("Failed to check project status")
                
                project = await response.json()
                status = project.get("status")
                
                if status == "completed":
                    # Extract audio URL from project
                    return project.get("audio_url")
                elif status == "failed":
                    raise RuntimeError("Audio generation failed")
                
                # Wait before next check
                await asyncio.sleep(delay_seconds)
        
        raise RuntimeError("Audio generation timed out")
    
    async def _download_audio(
        self, 
        session: aiohttp.ClientSession, 
        audio_url: str, 
        output_path: str
    ) -> None:
        """Download audio file from URL."""
        async with session.get(audio_url) as response:
            if response.status != 200:
                raise RuntimeError("Failed to download audio")
            
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write audio data
            with open(output_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
    
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