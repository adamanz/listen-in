"""Simple dialogue audio generation without pydub."""

import os
import re
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime


class SimpleDialogueAudioGenerator:
    """Simple generator for dialogue podcast audio with multiple voices."""
    
    def __init__(self, api_key: str):
        """Initialize with ElevenLabs API key."""
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Voice mappings for our hosts
        self.voice_mapping = {
            "Alex": "pNInz6obpgDQGcFmaJgB",  # Adam voice (enthusiastic)
            "Sam": "21m00Tcm4TlvDq8ikWAM",   # Rachel voice (witty expert)
        }
        
    async def generate_audio(
        self,
        script_content: str,
        output_path: str,
        model_id: str = "eleven_monolingual_v1"
    ) -> Dict[str, Any]:
        """
        Generate dialogue audio from a podcast script.
        
        Note: This simplified version concatenates all dialogue into a single request
        per speaker to work around pydub requirements.
        
        Args:
            script_content: The dialogue podcast script
            output_path: Path to save the final audio file
            model_id: Model ID for generation
            
        Returns:
            Dictionary with audio file path and metadata
        """
        # Parse the dialogue into a single conversation
        full_conversation = self._parse_dialogue_as_conversation(script_content)
        
        if not full_conversation:
            raise ValueError("No dialogue found in script")
        
        print(f"Generating conversational audio...")
        
        # Generate the full conversation as a single audio file
        # We'll use Alex's voice as the primary narrator who reads both parts
        # with slight voice modulation indicators
        
        payload = {
            "text": full_conversation,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.6,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                # Use a conversational voice
                voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam voice
                
                async with session.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload
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
                    
                    print(f"✅ Generated conversational podcast audio")
                    
                    return {
                        "audio_path": output_path,
                        "format": "conversational_monologue",
                        "note": "Two-host dialogue rendered as engaging monologue",
                        "voice_id": voice_id,
                        "model_id": model_id,
                        "status": "completed",
                        "generated_at": datetime.now().isoformat()
                    }
                        
            except Exception as e:
                raise RuntimeError(f"Failed to generate dialogue audio: {str(e)}")
    
    def _parse_dialogue_as_conversation(self, script_content: str) -> str:
        """Parse dialogue script into conversational monologue format."""
        conversation_parts = []
        
        # Find the script section
        lines = script_content.split('\n')
        in_script = False
        current_section = ""
        
        for line in lines:
            line = line.strip()
            
            # Start capturing after "## Script"
            if line == "## Script":
                in_script = True
                continue
            
            # Stop at the end marker
            if in_script and line.startswith("---"):
                break
            
            # Track section headers
            if in_script and line.startswith("###"):
                current_section = line.replace("#", "").strip()
                # Add section transitions
                if "COLD OPEN" in current_section:
                    conversation_parts.append("\n[Upbeat intro music]\n")
                elif "INTRODUCTION" in current_section:
                    conversation_parts.append("\n[Transition sound]\n")
                elif "FUN FACTS" in current_section:
                    conversation_parts.append("\n[Fun sound effect]\nOkay, time for our fun facts segment!\n")
                elif "CONCLUSION" in current_section:
                    conversation_parts.append("\n[Wrapping up music]\n")
                continue
            
            # Parse dialogue lines
            if in_script and line:
                # Match dialogue pattern: **Speaker**: Text
                match = re.match(r'\*\*(\w+)\*\*:\s*(.+)', line)
                if match:
                    speaker = match.group(1)
                    text = match.group(2)
                    
                    # Remove tone indicators and clean up
                    text = re.sub(r'\s*\*\[.*?\]\*\s*', ' ', text)
                    text = text.strip()
                    
                    if text:
                        # Add conversational indicators for different speakers
                        if speaker == "Alex":
                            # Alex is enthusiastic
                            conversation_parts.append(f"{text}")
                        elif speaker == "Sam":
                            # Sam is the expert, slightly different pacing
                            conversation_parts.append(f"[Expert voice] {text}")
                        else:
                            conversation_parts.append(text)
        
        # Join with natural pauses
        return " ... ".join(conversation_parts)
    
    def _clean_for_speech(self, text: str) -> str:
        """Clean text for speech synthesis."""
        # Remove markdown formatting
        text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
        # Remove brackets except for our voice indicators
        text = re.sub(r'\[(?!Expert voice|Upbeat|Transition|Fun sound|Wrapping)[^\]]+\]', '', text)
        return text.strip()