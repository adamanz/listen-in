"""FastMCP server for Listen-in podcast script generation."""

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from pathlib import Path
from datetime import datetime

from .parsers.text_parser import TextParser
from .generators.monologue_generator import MonologueGenerator
from .generators.o3_generator import O3Generator
from .generators.agent_generator import AgentGenerator
from .generators.audio_generator import AudioGenerator
from .generators.dialogue_generator import DialogueGenerator
from .generators.simple_dialogue_audio import SimpleDialogueAudioGenerator
from .utils.file_utils import save_script
from .config import (
    OPENAI_API_KEY, 
    ELEVENLABS_API_KEY,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TONE,
    DEFAULT_AUDIENCE,
    PODCAST_VOICES
)

# Create the FastMCP server instance
mcp = FastMCP(
    name="listen-in",
    instructions="""
    This server transforms local documents into engaging podcast scripts.
    
    Currently supports:
    - Text files (.txt)
    - Monologue-style scripts
    
    Use the generate_podcast_script tool to process documents.
    """
)

# Configuration model
class PodcastConfig(BaseModel):
    """Configuration for podcast generation."""
    openai_api_key: str = Field(description="OpenAI API key for GPT access")
    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key for audio generation")
    output_dir: str = Field(default="output", description="Directory for generated scripts")
    default_tone: str = Field(default="conversational", description="Default tone for scripts")
    default_audience: str = Field(default="general", description="Default target audience")

# Store configuration
config: Optional[PodcastConfig] = None

# Auto-configure from environment if available
def auto_configure():
    """Auto-configure from environment variables if available."""
    global config
    if OPENAI_API_KEY:
        config = PodcastConfig(
            openai_api_key=OPENAI_API_KEY,
            elevenlabs_api_key=ELEVENLABS_API_KEY,
            output_dir=str(DEFAULT_OUTPUT_DIR),
            default_tone=DEFAULT_TONE,
            default_audience=DEFAULT_AUDIENCE
        )
        # Create output directory
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Try auto-configuration on import
auto_configure()

@mcp.tool
async def configure(
    openai_api_key: Optional[str] = None,
    elevenlabs_api_key: Optional[str] = None,
    output_dir: Optional[str] = None,
    default_tone: str = "conversational",
    default_audience: str = "general"
) -> str:
    """Configure the Listen-in server with necessary settings."""
    global config
    
    # Use environment variables as defaults
    final_openai_key = openai_api_key or OPENAI_API_KEY
    final_elevenlabs_key = elevenlabs_api_key or ELEVENLABS_API_KEY
    final_output_dir = output_dir or str(DEFAULT_OUTPUT_DIR)
    
    if not final_openai_key:
        raise ValueError("OpenAI API key is required. Set OPEN_AI_KEY in .env or provide via configure()")
    
    config = PodcastConfig(
        openai_api_key=final_openai_key,
        elevenlabs_api_key=final_elevenlabs_key,
        output_dir=final_output_dir,
        default_tone=default_tone,
        default_audience=default_audience
    )
    
    # Create output directory if it doesn't exist
    Path(final_output_dir).mkdir(parents=True, exist_ok=True)
    
    audio_status = "enabled" if final_elevenlabs_key else "disabled"
    return f"Listen-in configured successfully. Output directory: {final_output_dir}. Audio generation: {audio_status}"

@mcp.tool
async def generate_podcast_script(
    file_path: str,
    style: str = "monologue",
    tone: Optional[str] = None,
    audience: Optional[str] = None,
    custom_instructions: Optional[str] = None,
    model: str = "o3"
) -> dict:
    """
    Generate a podcast script from a local document.
    
    Args:
        file_path: Path to the input document
        style: Script style ('monologue' or 'dialogue')
        tone: Tone of the script (defaults to configured tone)
        audience: Target audience (defaults to configured audience)
        custom_instructions: Additional instructions for script generation
        model: Model to use ("o3" for gpt-4.1-mini via Agents SDK or "gpt-3.5-turbo")
        
    Returns:
        Dictionary with script_path and metadata
    """
    if not config:
        raise ValueError("Server not configured. Please run configure() first.")
    
    # Validate file exists
    input_path = Path(file_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    if input_path.suffix.lower() != '.txt':
        raise ValueError("Currently only .txt files are supported")
    
    # Parse the document
    parser = TextParser()
    content = parser.parse(file_path)
    
    # Generate the script with the selected model and style
    if style == "dialogue":
        generator = DialogueGenerator(api_key=config.openai_api_key)
    elif model == "o3":
        generator = AgentGenerator(api_key=config.openai_api_key)
    else:
        generator = MonologueGenerator(api_key=config.openai_api_key)
    
    script = await generator.generate(
        content=content,
        tone=tone or config.default_tone,
        audience=audience or config.default_audience,
        custom_instructions=custom_instructions
    )
    
    # Save the script
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{input_path.stem}_podcast_{timestamp}.md"
    output_path = Path(config.output_dir) / output_filename
    
    save_script(script, str(output_path))
    
    return {
        "script_path": str(output_path),
        "source_file": file_path,
        "style": style,
        "tone": tone or config.default_tone,
        "audience": audience or config.default_audience,
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool
async def list_generated_scripts() -> list[dict]:
    """List all generated podcast scripts."""
    if not config:
        raise ValueError("Server not configured. Please run configure() first.")
    
    output_dir = Path(config.output_dir)
    if not output_dir.exists():
        return []
    
    scripts = []
    for file in output_dir.glob("*_podcast_*.md"):
        scripts.append({
            "filename": file.name,
            "path": str(file),
            "size": file.stat().st_size,
            "created": datetime.fromtimestamp(file.stat().st_ctime).isoformat()
        })
    
    return sorted(scripts, key=lambda x: x["created"], reverse=True)

@mcp.tool
async def generate_podcast_audio(
    script_path: str,
    voice_mode: str = "bulletin",
    quality: str = "standard",
    duration_scale: str = "default",
    voice_id: Optional[str] = None,
    voice_name: Optional[str] = None,
    callback_url: Optional[str] = None
) -> dict:
    """
    Generate audio from a podcast script using ElevenLabs.
    
    Args:
        script_path: Path to the generated script file
        voice_mode: "bulletin" for monologue, "conversation" for dialogue
        quality: Audio quality (standard/high/ultra/ultra_lossless)
        duration_scale: Length preference (short/default/long)
        voice_id: Optional specific voice ID to use
        voice_name: Optional voice name (rachel/adam/bella/emily/jessica/matthew)
        callback_url: Optional webhook URL for async processing
        
    Returns:
        Dictionary with audio file information
    """
    if not config:
        raise ValueError("Server not configured. Please run configure() first.")
    
    if not config.elevenlabs_api_key:
        raise ValueError("ElevenLabs API key not configured. Audio generation is disabled.")
    
    # Validate script file exists
    script_file = Path(script_path)
    if not script_file.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")
    
    # Read the script content
    with open(script_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Generate audio filename based on script filename
    audio_filename = script_file.stem + ".mp3"
    audio_path = Path(config.output_dir) / audio_filename
    
    # Determine voice ID
    final_voice_id = voice_id
    if not final_voice_id and voice_name:
        # Look up voice ID by name
        final_voice_id = PODCAST_VOICES.get(voice_name.lower())
        if not final_voice_id:
            available_voices = ", ".join(PODCAST_VOICES.keys())
            raise ValueError(f"Unknown voice name: {voice_name}. Available: {available_voices}")
    
    # Check if it's a dialogue script by looking for dialogue markers
    is_dialogue = "**Alex**:" in script_content or "**Sam**:" in script_content
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Audio generation - is_dialogue: {is_dialogue}, script preview: {script_content[:200]}...")
    
    # Generate audio with appropriate generator
    if is_dialogue:
        generator = SimpleDialogueAudioGenerator(api_key=config.elevenlabs_api_key)
        result = await generator.generate_audio(
            script_content=script_content,
            output_path=str(audio_path)
        )
    else:
        generator = AudioGenerator(api_key=config.elevenlabs_api_key)
        result = await generator.generate_audio(
            script_content=script_content,
            output_path=str(audio_path),
            voice_mode=voice_mode,
            quality=quality,
            duration_scale=duration_scale,
            voice_id=final_voice_id,
            callback_url=callback_url
        )
    
    result["script_path"] = script_path
    return result

@mcp.tool
async def list_available_voices() -> Dict[str, Any]:
    """List available voices for podcast generation."""
    # First show preset voices
    preset_voices = {
        "preset_voices": {
            name: {
                "voice_id": voice_id,
                "description": f"Preset voice for {name.capitalize()}"
            }
            for name, voice_id in PODCAST_VOICES.items()
        }
    }
    
    # If ElevenLabs is configured, also fetch available voices
    if config and config.elevenlabs_api_key:
        try:
            generator = AudioGenerator(api_key=config.elevenlabs_api_key)
            api_voices = await generator.get_voices()
            
            preset_voices["elevenlabs_voices"] = [
                {
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", "unknown"),
                    "preview_url": voice.get("preview_url", "")
                }
                for voice in api_voices[:10]  # Limit to first 10
            ]
        except Exception as e:
            preset_voices["elevenlabs_voices"] = f"Error fetching voices: {str(e)}"
    else:
        preset_voices["elevenlabs_voices"] = "Configure ElevenLabs API key to see all available voices"
    
    return preset_voices

if __name__ == "__main__":
    # Run the server
    mcp.run()