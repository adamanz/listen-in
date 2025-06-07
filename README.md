# Listen-in

Transform local documents into engaging podcast scripts using AI.

## Overview

Listen-in is a proof-of-concept MCP (Model Context Protocol) server that reads local documents and generates natural, conversational podcast scripts using OpenAI's API. Built with FastMCP for seamless integration with AI assistants like Claude.

## Features

- 📄 Support for text files (.txt) with more formats coming soon
- 🎙️ Generate monologue-style podcast scripts
- 🤖 Powered by OpenAI's o3 model
- 💾 Save scripts as local markdown files
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
# First, configure with your OpenAI API key
configure(
    openai_api_key="your-api-key",
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

4. List generated scripts:
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
└── tests/                 # Test suite
```

## Development

- Python 3.9+ required
- Uses FastMCP for MCP server implementation
- Modular architecture for easy extension
- See [CLAUDE.md](CLAUDE.md) for development guidelines
- See [spec.md](spec.md) for detailed specification

## Roadmap

- [x] Phase 1: Basic text file support with monologue generation
- [ ] Phase 2: PDF/DOCX support, dialogue generation
- [ ] Phase 3: Batch processing, advanced formatting

## Contributing

This is a proof-of-concept project. Feel free to explore and extend!

## License

MIT