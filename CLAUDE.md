# CLAUDE.md - Listen-in Project Guidelines

## Project Focus
Listen-in is a POC that transforms local documents into podcast scripts using OpenAI's SDK. The goal is to create natural, engaging audio content from written materials.

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

## Next Steps
1. Choose implementation language (TypeScript recommended)
2. Set up project structure and dependencies
3. Implement basic document reading
4. Create OpenAI integration
5. Build script generation logic

## Notes for Development
- Keep API keys secure (use environment variables)
- Add examples of input documents and generated scripts
- Document prompt engineering decisions
- Track performance metrics (processing time, token usage)