"""Dialogue audio generation with multiple voices using ElevenLabs."""

import os
import re
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
import tempfile
from pydub import AudioSegment


class DialogueAudioGenerator:
    """Generator for dialogue podcast audio with multiple voices."""
    
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
        model_id: str = "eleven_monolingual_v1",
        voice_settings: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Generate dialogue audio from a podcast script.
        
        Args:
            script_content: The dialogue podcast script
            output_path: Path to save the final audio file
            model_id: Model ID for generation
            voice_settings: Optional voice settings override
            
        Returns:
            Dictionary with audio file path and metadata
        """
        # Parse the dialogue into segments
        dialogue_segments = self._parse_dialogue(script_content)
        
        if not dialogue_segments:
            raise ValueError("No dialogue segments found in script")
        
        # Default voice settings for more natural conversation
        if not voice_settings:
            voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.4,
                "use_speaker_boost": True
            }
        
        # Generate audio for each segment
        temp_files = []
        
        try:
            print(f"Generating audio for {len(dialogue_segments)} dialogue segments...")
            
            # Process segments in batches to avoid rate limits
            batch_size = 5
            for i in range(0, len(dialogue_segments), batch_size):
                batch = dialogue_segments[i:i+batch_size]
                batch_tasks = []
                
                for j, (speaker, text) in enumerate(batch):
                    voice_id = self.voice_mapping.get(speaker)
                    if not voice_id:
                        raise ValueError(f"Unknown speaker: {speaker}")
                    
                    # Create temporary file for this segment
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                    temp_files.append(temp_file.name)
                    temp_file.close()
                    
                    # Add task to generate this segment
                    task = self._generate_segment(
                        text=text,
                        voice_id=voice_id,
                        output_path=temp_file.name,
                        model_id=model_id,
                        voice_settings=voice_settings,
                        segment_index=i+j,
                        total_segments=len(dialogue_segments)
                    )
                    batch_tasks.append(task)
                
                # Generate batch concurrently
                await asyncio.gather(*batch_tasks)
                
                # Small delay between batches to avoid rate limits
                if i + batch_size < len(dialogue_segments):
                    await asyncio.sleep(1)
            
            # Combine all audio segments
            print("Combining audio segments...")
            self._combine_audio_segments(temp_files, output_path)
            
            # Calculate total duration
            final_audio = AudioSegment.from_mp3(output_path)
            duration_seconds = len(final_audio) / 1000
            
            return {
                "audio_path": output_path,
                "total_segments": len(dialogue_segments),
                "duration_seconds": duration_seconds,
                "duration_minutes": round(duration_seconds / 60, 1),
                "speakers": list(self.voice_mapping.keys()),
                "status": "completed",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate dialogue audio: {str(e)}")
        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def _parse_dialogue(self, script_content: str) -> List[Tuple[str, str]]:
        """Parse dialogue script into (speaker, text) tuples."""
        segments = []
        
        # Find the script section
        lines = script_content.split('\n')
        in_script = False
        
        for line in lines:
            line = line.strip()
            
            # Start capturing after "## Script"
            if line == "## Script":
                in_script = True
                continue
            
            # Stop at the end marker
            if in_script and line.startswith("---"):
                break
            
            # Parse dialogue lines
            if in_script and line:
                # Skip section headers
                if line.startswith("###"):
                    continue
                
                # Match dialogue pattern: **Speaker**: Text
                match = re.match(r'\*\*(\w+)\*\*:\s*(.+)', line)
                if match:
                    speaker = match.group(1)
                    text = match.group(2)
                    
                    # Remove tone indicators and clean up
                    text = re.sub(r'\s*\*\[.*?\]\*\s*', ' ', text)
                    text = text.strip()
                    
                    if text and speaker in self.voice_mapping:
                        segments.append((speaker, text))
        
        return segments
    
    async def _generate_segment(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        model_id: str,
        voice_settings: Dict[str, float],
        segment_index: int,
        total_segments: int
    ) -> None:
        """Generate audio for a single dialogue segment."""
        # Add subtle pauses for natural conversation flow
        if segment_index > 0:
            text = "... " + text
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"ElevenLabs API error for segment {segment_index+1}: {response.status} - {error_text}")
                
                # Write audio data
                with open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                
                print(f"✓ Generated segment {segment_index+1}/{total_segments}")
    
    def _combine_audio_segments(self, temp_files: List[str], output_path: str) -> None:
        """Combine multiple audio segments into one file."""
        combined = AudioSegment.empty()
        
        # Add a short silence between segments for natural pacing
        silence = AudioSegment.silent(duration=300)  # 300ms pause
        
        for i, temp_file in enumerate(temp_files):
            segment = AudioSegment.from_mp3(temp_file)
            
            if i > 0:
                # Add natural pause between speakers
                combined += silence
            
            combined += segment
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Export combined audio
        combined.export(output_path, format="mp3", bitrate="128k")
        print(f"✅ Combined {len(temp_files)} segments into {output_path}")