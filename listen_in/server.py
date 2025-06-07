"""FastMCP server for Listen-in podcast script generation."""

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional
import os
from pathlib import Path
from datetime import datetime

from .parsers.text_parser import TextParser
from .generators.monologue_generator import MonologueGenerator
from .utils.file_utils import save_script

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
    output_dir: str = Field(default="output", description="Directory for generated scripts")
    default_tone: str = Field(default="conversational", description="Default tone for scripts")
    default_audience: str = Field(default="general", description="Default target audience")

# Store configuration
config: Optional[PodcastConfig] = None

@mcp.tool
async def configure(
    openai_api_key: str,
    output_dir: str = "output",
    default_tone: str = "conversational",
    default_audience: str = "general"
) -> str:
    """Configure the Listen-in server with necessary settings."""
    global config
    
    config = PodcastConfig(
        openai_api_key=openai_api_key,
        output_dir=output_dir,
        default_tone=default_tone,
        default_audience=default_audience
    )
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    return f"Listen-in configured successfully. Output directory: {output_dir}"

@mcp.tool
async def generate_podcast_script(
    file_path: str,
    style: str = "monologue",
    tone: Optional[str] = None,
    audience: Optional[str] = None,
    custom_instructions: Optional[str] = None
) -> dict:
    """
    Generate a podcast script from a local document.
    
    Args:
        file_path: Path to the input document
        style: Script style (currently only 'monologue' supported)
        tone: Tone of the script (defaults to configured tone)
        audience: Target audience (defaults to configured audience)
        custom_instructions: Additional instructions for script generation
        
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
    
    # Generate the script
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

if __name__ == "__main__":
    # Run the server
    mcp.run()