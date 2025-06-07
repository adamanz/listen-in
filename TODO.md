# MCP Podcast Server with x402 Payments - TODO List

## Architecture Overview
- **FastMCP Server (Python)**: Main MCP server handling ElevenLabs API integration
- **x402 Payment Service (TypeScript)**: HTTP service handling payment verification/settlement
- **Communication**: HTTP bridge between Python MCP server and TypeScript payment service

## Phase 1: Project Setup ✅
- [x] Create project structure
- [x] Create TODO list
- [ ] Set up Python environment with FastMCP
- [ ] Set up TypeScript environment for x402 payment service
- [ ] Create docker-compose for running both services

## Phase 2: Basic FastMCP Server
- [ ] Create basic FastMCP server template
- [ ] Add configuration management (API keys, endpoints)
- [ ] Implement health check tool
- [ ] Set up logging and error handling
- [ ] Create MCP client for testing

## Phase 3: x402 Payment Service (TypeScript)
- [ ] Initialize TypeScript project with Express
- [ ] Integrate x402 SDK
- [ ] Create `/verify` endpoint for payment verification
- [ ] Create `/settle` endpoint for payment settlement
- [ ] Add configuration for:
  - Facilitator URL
  - Payment recipient address
  - Supported assets and networks
- [ ] Implement rate limiting and security

## Phase 4: Payment Integration Bridge
- [ ] Create Python HTTP client for payment service
- [ ] Implement payment decorator for FastMCP tools
- [ ] Add payment requirement metadata to tools
- [ ] Handle payment flow:
  - Check if tool requires payment
  - Request payment verification
  - Execute tool on successful payment
  - Return payment receipt with result

## Phase 5: ElevenLabs Integration
- [ ] Add ElevenLabs Python SDK
- [ ] Implement voice listing tool
- [ ] Implement text-to-speech tool
- [ ] Add voice cloning capabilities
- [ ] Create podcast generation workflow:
  - Parse input documents (PDFs, code)
  - Generate script/dialogue
  - Convert to speech
  - Merge audio segments

## Phase 6: Document Processing Tools
- [ ] PDF text extraction tool
- [ ] Code repository analysis tool
- [ ] Content summarization tool
- [ ] Script generation tool
- [ ] Dialogue formatting tool

## Phase 7: Audio Processing Tools
- [ ] Audio file management
- [ ] Audio merging/concatenation
- [ ] Add intro/outro music
- [ ] Audio format conversion
- [ ] Upload to storage (S3/GCS)

## Phase 8: Advanced Features
- [ ] Multi-voice conversations
- [ ] Background music integration
- [ ] Audio effects and transitions
- [ ] Chapter markers generation
- [ ] Transcript generation

## Phase 9: Testing & Documentation
- [ ] Unit tests for FastMCP tools
- [ ] Integration tests for payment flow
- [ ] End-to-end podcast generation test
- [ ] API documentation
- [ ] User guide
- [ ] Example clients

## Phase 10: Deployment
- [ ] Dockerize all services
- [ ] Create Kubernetes manifests
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring/logging
- [ ] Deploy to cloud provider

## Configuration Requirements
### FastMCP Server (Python)
- ElevenLabs API key
- Payment service URL
- Storage credentials (S3/GCS)
- Rate limits

### x402 Payment Service (TypeScript)
- Ethereum wallet private key
- Facilitator URL
- Accepted tokens/chains
- Price per tool call

## Key Decisions to Make
1. **Storage Solution**: S3, GCS, or local storage for audio files?
2. **Payment Amounts**: How much to charge per tool/operation?
3. **Audio Quality**: Sample rates, bit rates, formats?
4. **Script Generation**: Use LLM API or built-in prompts?
5. **Caching Strategy**: Cache generated audio segments?

## Security Considerations
- [ ] Secure API key storage
- [ ] Payment verification before tool execution
- [ ] Rate limiting per user/API key
- [ ] Input validation for all tools
- [ ] Secure file handling
- [ ] CORS configuration for payment service 