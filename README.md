# ElevenLabs MCP Server

A simple FastMCP server that provides text-to-speech capabilities using the ElevenLabs API.

## Features

- **List Voices**: Get all available ElevenLabs voices
- **Text-to-Speech**: Convert text to high-quality speech audio
- **Voice Settings**: Get default settings for specific voices
- **API Status Check**: Verify your ElevenLabs API configuration

## Setup

1. Install dependencies using `uv` (or `pip`):
```bash
uv pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add your ElevenLabs API key:
```bash
cp env.example .env
# Edit .env and add your API key
```

3. Get your ElevenLabs API key from: https://elevenlabs.io/app/speech-synthesis/settings

## Running the Server

### As a standalone server (STDIO transport):
```bash
python elevenlabs_server.py
```

### Using FastMCP CLI:
```bash
fastmcp run elevenlabs_server.py
```

### With HTTP transport:
```bash
fastmcp run elevenlabs_server.py --transport streamable-http --port 8000
```

## Testing

Run the test client to verify everything is working:
```bash
python test_elevenlabs.py
```

## Available Tools

### `list_voices`
Lists all available ElevenLabs voices with their IDs and descriptions.

### `text_to_speech`
Converts text to speech with customizable parameters:
- `text`: The text to convert
- `voice_id`: Voice to use (defaults to Rachel)
- `model_id`: ElevenLabs model (monolingual, multilingual, or turbo)
- `stability`: Voice stability (0-1)
- `similarity_boost`: Voice clarity (0-1)

Returns base64-encoded MP3 audio data.

### `get_voice_settings`
Gets the default settings for a specific voice ID.

### `check_api_status`
Verifies your API key is configured and working.

## Resources

The server also exposes a resource at `resource://voices/list` that provides the raw voice data.

## Using with Claude Desktop

To use this server with Claude Desktop, you can either:

1. Install it using FastMCP CLI:
```bash
fastmcp install elevenlabs_server.py
```

2. Or manually add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "python",
      "args": ["/path/to/elevenlabs_server.py"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Next Steps

This is a basic implementation. You could extend it with:
- Voice cloning capabilities
- Audio file management
- Streaming audio support
- Speech-to-speech conversion
- Project and history management 