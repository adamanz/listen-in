# ElevenLabs Integration Summary

## Overview
ElevenLabs provides text-to-speech and conversational AI capabilities. For Listen-in, we'll use their Podcast API to convert generated scripts into audio.

## Key Features for Listen-in

### Podcast Generation API
- **Endpoint**: POST to ElevenLabs API
- **Modes**: 
  - `conversation`: Two-voice dialogue
  - `bulletin`: Single voice monologue (perfect for our current implementation)
- **Quality Options**:
  - `standard`: 128kbps (default)
  - `high`: 192kbps (+20% cost)
  - `ultra`: 192kbps highest quality (+50% cost)
  - `ultra_lossless`: 705.6kbps (+100% cost)
- **Duration Scale**: `short` (<3min), `default` (3-7min), `long` (>7min)

### API Requirements
- **Authentication**: `xi-api-key` header
- **Model ID**: Required (query GET /v1/models for available models)
- **Source Content**: Text or document input
- **Language**: Two-letter ISO code (optional)

### Cost Structure
- LLM costs currently covered by ElevenLabs
- Audio generation costs charged to user
- Future: Both LLM and audio costs charged

### Response Format
Returns a project object with:
- Project ID
- Status
- Audio URL (when complete)
- Conversion metadata

### Callback Support
Optional webhook URL for async processing notifications

## Integration Strategy for Listen-in

1. **Add ElevenLabs SDK**: `pip install elevenlabs`
2. **New Tool**: `generate_podcast_audio` in FastMCP server
3. **Configuration**: Store ElevenLabs API key
4. **Workflow**:
   - Generate script with OpenAI
   - Convert script to audio with ElevenLabs
   - Save audio file locally
   - Return both script and audio paths

## Example Implementation
```python
async def generate_podcast_audio(
    script_path: str,
    voice_mode: str = "bulletin",  # monologue
    quality: str = "standard",
    duration: str = "default"
) -> dict:
    # Read script
    # Call ElevenLabs API
    # Save audio file
    # Return audio path and metadata
```

## Benefits
- Professional voice synthesis
- Multiple voice options
- High-quality audio output
- Async processing support
- Built-in podcast optimization