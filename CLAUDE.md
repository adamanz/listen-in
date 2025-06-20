# CLAUDE.md - Listen-in Project Guidelines

Use OpenAI Agent SDK /Users/adamanzuoni/listen-in/ai-docs/openai-sdk.md and o3-2025-04-16 model

## O3 Model Usage
The project uses the o3-2025-04-16 model which requires specific API syntax:

### Node.js/JavaScript (Preferred)
```javascript
import OpenAI from "openai";
const client = new OpenAI({ apiKey: process.env.OPEN_AI_KEY });

const response = await client.responses.create({
    model: "o3-2025-04-16",
    input: "Your prompt here"
});

console.log(response.output_text);
```

### Python (if needed)
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))

response = client.responses.create(
    model="o3-2025-04-16", 
    input="Your prompt here"
)

print(response.output_text)
```

**Important Notes:**
- Use `responses.create()` NOT `chat.completions.create()`
- Use `input` parameter NOT `messages`
- Use `output_text` property for response
- Model does not support temperature or max_tokens parameters
- API key in .env file is `OPEN_AI_KEY` 

## Project Focus
Listen-in is a POC that transforms local documents into podcast scripts using OpenAI's Agnet /Users/adamanzuoni/listen-in/ai-docs/openai-sdk.mdSDK. The goal is to create natural, engaging audio content from written materials.

## Key Objectives
1. Build a functional CLI tool that processes documents
2. Generate conversational, natural-sounding podcast scripts
3. Maintain content accuracy while improving accessibility
4. Create a solid foundation for future audio content generation

## Technical Priorities
- Clean, modular code architecture
- Efficient OpenAI API usage
- Robust error handling
- Clear documentation 

## Development Guidelines
- Start with simple text/markdown support before complex formats
- Focus on script quality over feature quantity
- Test with diverse document types (technical, narrative, educational)
- Keep the POC scope manageable - avoid feature creep

## Testing Approach
- Test with sample documents of varying lengths
- Verify script readability and natural flow
- Check accuracy of content transformation
- Monitor API usage and costs

## Current Phase
Phase 1: Basic Implementation
- Setting up project structure
- Basic file reading capabilities
- OpenAI integration
- Simple monologue script generation

## Important Commands
```bash
# Install dependencies (once package.json is created)
npm install

# Run the application (once implemented)
npm run start

# Run tests (once implemented)
npm test

# Lint code
npm run lint

# Type check
npm run typecheck
```

## File Structure
```
listen-in/
├── spec.md           # POC specification
├── CLAUDE.md         # This file - project guidelines
├── src/              # Source code
│   ├── index.ts      # Main entry point
│   ├── parsers/      # Document parsers
│   ├── generators/   # Script generators
│   └── utils/        # Utility functions
├── examples/         # Example documents and outputs
└── tests/           # Test files
```


## Notes for Development
- Keep API keys secure (use environment variables)
- Add examples of input documents and generated scripts
- Document prompt engineering decisions
- Track performance metrics (processing time, token usage)