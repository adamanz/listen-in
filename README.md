# Listen-in

Transform local documents into engaging podcast scripts using AI.

## Overview

Listen-in is a proof-of-concept MCP (Model Context Protocol) server that reads local documents and generates natural, conversational podcast scripts using OpenAI's API. Built with FastMCP for seamless integration with AI assistants like Claude.

## Features

- 📄 Support for text files (.txt) with more formats coming soon
- 🎙️ Generate monologue-style podcast scripts
- 🎧 Convert scripts to audio with ElevenLabs integration
- 🤖 Powered by OpenAI's o3 model
- 🎵 Multiple voice options and quality levels
- 💾 Save scripts and audio files locally
- 🔧 Configurable through MCP server tools
- 🚀 FastMCP server for easy integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adamanz/listen-in.git
cd listen-in
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### As a FastMCP Server

1. Start the server:
```bash
python -m listen_in.server
```

2. Configure the server (in your MCP client):
```python
# Configure with your API keys
configure(
    openai_api_key="your-openai-key",
    elevenlabs_api_key="your-elevenlabs-key",  # Optional
    output_dir="output",
    default_tone="conversational",
    default_audience="general"
)
```

3. Generate a podcast script:
```python
# Generate a script from a text file
result = generate_podcast_script(
    file_path="path/to/document.txt",
    style="monologue",
    tone="educational",
    audience="beginner"
)
```

4. Convert script to audio:
```python
# Generate audio with default voice (Rachel)
audio_result = generate_podcast_audio(
    script_path=result["script_path"],
    voice_mode="bulletin",
    quality="high",
    duration_scale="default"
)

# Or specify a voice by name
audio_result = generate_podcast_audio(
    script_path=result["script_path"],
    voice_name="adam",  # Options: rachel, adam, bella, emily, jessica, matthew
    quality="ultra"
)

# Or use a specific voice ID
audio_result = generate_podcast_audio(
    script_path=result["script_path"],
    voice_id="21m00Tcm4TlvDq8ikWAM"
)
```

5. List available voices:
```python
# See preset voices and ElevenLabs voices
voices = list_available_voices()
```

6. List generated scripts:
```python
# See all generated scripts
scripts = list_generated_scripts()
```

### MCP Integration with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "listen-in": {
      "command": "python",
      "args": ["-m", "listen_in.server"],
      "cwd": "/path/to/listen-in"
    }
  }
}
```

## Project Structure

```
listen-in/
├── listen_in/             # Main package
│   ├── server.py          # FastMCP server
│   ├── parsers/           # Document parsers
│   ├── generators/        # Script generators
│   └── utils/             # Utilities
├── output/                # Generated scripts
├── examples/              # Example documents
│   ├── sample_article.txt # Remote work article
│   └── gdpr_excerpt.txt   # GDPR regulation excerpt
├── example-script/        # Example generated scripts
│   └── gdpr_podcast_script.txt
└── tests/                 # Test suite
```

## Example Output

Check out `example-script/gdpr_podcast_script.txt` to see how Listen-in transforms a complex legal document (GDPR) into an engaging, conversational podcast script with natural speech patterns, transitions, and emphasis markers.

## Development

- Python 3.9+ required
- Uses FastMCP for MCP server implementation
- Modular architecture for easy extension
- See [CLAUDE.md](CLAUDE.md) for development guidelines
- See [spec.md](spec.md) for detailed specification

## Roadmap

- [x] Phase 1: Basic text file support with monologue generation
- [x] ElevenLabs audio generation integration
- [ ] Phase 2: PDF/DOCX support, dialogue generation
- [ ] Phase 3: Batch processing, advanced formatting
- [ ] Future: Background music, sound effects, chapter markers

## Contributing

This is a proof-of-concept project. Feel free to explore and extend!

## License

MIT