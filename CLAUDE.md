# CLAUDE.md - Listen-in Project Guidelines

## Project Focus
Listen-in is a POC that transforms local documents into podcast scripts using OpenAI's SDK. The goal is to create natural, engaging audio content from written materials. Built as a FastMCP server for easy integration with AI assistants.

## Key Objectives
1. Build a functional FastMCP server that processes documents
2. Generate conversational, natural-sounding podcast scripts
3. Maintain content accuracy while improving accessibility
4. Create a solid foundation for future audio content generation

## Technical Stack
- **Language**: Python 3.9+
- **Framework**: FastMCP
- **AI Model**: OpenAI o3
- **Architecture**: Modular design with separate parsers, generators, and utilities

## Development Guidelines
- Start with simple text support before complex formats
- Focus on script quality over feature quantity
- Test with diverse document types (technical, narrative, educational)
- Keep the POC scope manageable - avoid feature creep

## Testing Approach
- Test with sample documents of varying lengths
- Verify script readability and natural flow
- Check accuracy of content transformation
- Monitor API usage and costs

## Current Phase
Phase 1: Basic Implementation ✅ (In Progress)
- ✅ Python FastMCP project structure
- ✅ Basic FastMCP server with configuration
- ✅ Text file parser implementation
- 🔄 OpenAI integration for o3 model
- 🔄 Monologue script generator
- 🔄 File output functionality

## Important Commands
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastMCP server
python -m listen_in.server

# Run tests (once implemented)
pytest

# Format code
black listen_in/

# Lint code
ruff check listen_in/

# Type check
mypy listen_in/
```

## File Structure
```
listen-in/
├── spec.md                # POC specification
├── CLAUDE.md              # This file - project guidelines
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── .gitignore             # Git ignore patterns
├── listen_in/             # Python package
│   ├── __init__.py
│   ├── server.py          # FastMCP server entry point
│   ├── parsers/           # Document parsers
│   │   ├── __init__.py
│   │   └── text_parser.py # Text file parser
│   ├── generators/        # Script generators
│   │   ├── __init__.py
│   │   └── monologue_generator.py
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── file_utils.py
├── output/                # Generated scripts (gitignored)
├── examples/              # Example documents
└── tests/                 # Test files
```

## Next Steps
1. Complete OpenAI integration with o3 model
2. Implement monologue script generator
3. Add file output functionality
4. Test with example documents
5. Add error handling and validation

## MCP Server Tools
The FastMCP server exposes the following tools:

### `configure`
Configure the server with OpenAI API key and settings.
- `openai_api_key`: Required OpenAI API key
- `output_dir`: Directory for generated scripts (default: "output")
- `default_tone`: Default tone for scripts (default: "conversational")
- `default_audience`: Default target audience (default: "general")

### `generate_podcast_script`
Generate a podcast script from a document.
- `file_path`: Path to input document (currently .txt only)
- `style`: Script style (currently only "monologue")
- `tone`: Optional tone override
- `audience`: Optional audience override
- `custom_instructions`: Additional generation instructions

### `list_generated_scripts`
List all previously generated podcast scripts.

## Prompt Engineering Strategy

The quality of generated podcast scripts heavily depends on well-crafted prompts. Our approach uses a multi-layered prompting strategy:

### System Prompts

System prompts establish the AI's role and core behavior. Key elements:

1. **Role Definition**: "You are a professional podcast script writer"
2. **Style Guidelines**: Specific instructions for tone (conversational, educational, etc.)
3. **Audience Adaptation**: Instructions for target audience level
4. **Speech Patterns**: Natural transitions, rhetorical questions, personal connections
5. **Structural Elements**: Hook, transitions, conclusions
6. **Audio Optimization**: Short sentences, active voice, pause markers

### Dynamic Prompt Construction

Prompts are built dynamically based on:
- Document type and structure
- Desired output format (monologue, dialogue)
- Target audience (general, beginner, expert)
- Tone preferences (conversational, professional, casual)

### Key Prompt Components

1. **Tone Guides**:
   - Conversational: "friendly, engaging, and natural as if talking to a friend"
   - Educational: "clear, informative, and structured for learning"
   - Professional: "polished, authoritative, and business-appropriate"
   - Casual: "relaxed, informal, and entertaining"

2. **Audience Guides**:
   - General: "accessible to anyone with basic knowledge"
   - Beginner: "simple explanations, avoid jargon, define terms"
   - Expert: "technical depth is welcome, assume domain knowledge"
   - Young: "energetic, relatable examples, shorter sentences"

3. **Structural Markers**:
   - `[PAUSE]`: Natural breathing points
   - `[EMPHASIS]`: Vocal emphasis for key points
   - Time estimates for sections
   - Transitions between topics

### Prompt Templates

Example monologue generation prompt structure:
```
Transform this document into an engaging podcast monologue script.

Document Title: {title}
Word Count: {word_count}
Estimated Speaking Time: {duration} minutes

Document Content:
---
{content}
---

Requirements:
1. Natural, flowing monologue
2. Engaging introduction hook
3. Smooth topic transitions
4. [PAUSE] and [EMPHASIS] markers
5. Memorable conclusion
6. Maintain source accuracy
```

### Future Prompt Enhancements

- Few-shot examples for better consistency
- Chain-of-thought processing for complex documents
- Style-specific prompt templates
- Custom prompt injection support
- Multi-language prompt variations

## Notes for Development
- Keep API keys secure (configured through MCP server)
- Add examples of input documents and generated scripts
- Document prompt engineering decisions and test results
- Track performance metrics (processing time, token usage)
- Consider adding streaming support for large documents
- Test prompts with diverse document types
- Iterate on prompts based on output quality