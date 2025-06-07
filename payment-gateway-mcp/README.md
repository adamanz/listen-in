# ElevenLabs Payment Gateway MCP Server

This TypeScript MCP server acts as a payment gateway wrapper for the ElevenLabs Python MCP server, implementing x402 protocol to charge users 10 cents per tool call.

## Architecture

```
Claude Desktop → Payment Gateway (TypeScript) → ElevenLabs Server (Python)
                 Handles x402 payments            Handles TTS operations
```

## Setup

### 1. Install Dependencies

```bash
cd payment-gateway-mcp
npm install
```

### 2. Configure Environment Variables

Create a `.env` file based on the following template:

```env
# User's private key for making payments (NEVER use a key with mainnet funds in development)
USER_PRIVATE_KEY=0x...

# Your wallet address to receive payments
PAYMENT_RECIPIENT=0x...

# URL of the ElevenLabs Python server
ELEVENLABS_SERVER_URL=http://localhost:8000

# Price per tool call in USD
PRICE_PER_CALL=0.10

# x402 configuration (optional)
X402_RESOURCE_SERVER_URL=https://x402.org/facilitator
X402_NETWORK=base-sepolia
```

### 3. Update ElevenLabs Python Server

The Python server needs to be updated to accept JSON-RPC style calls. We'll modify it to support the `/call` endpoint that the payment gateway expects.

### 4. Run Both Servers

First, start the ElevenLabs Python server:
```bash
cd ../
python elevenlabs_server.py
```

Then, start the payment gateway:
```bash
cd payment-gateway-mcp
npm run dev
```

### 5. Configure Claude Desktop

Update your Claude Desktop configuration to use the payment gateway:

```json
{
  "mcpServers": {
    "elevenlabs-paid": {
      "command": "node",
      "args": ["/absolute/path/to/payment-gateway-mcp/dist/index.js"],
      "env": {
        "USER_PRIVATE_KEY": "<user's payment wallet private key>",
        "PAYMENT_RECIPIENT": "<your wallet address>",
        "ELEVENLABS_SERVER_URL": "http://localhost:8000",
        "PRICE_PER_CALL": "0.10"
      }
    }
  }
}
```

## Available Tools

All tools charge $0.10 per call (configurable via PRICE_PER_CALL):

1. **list_voices** - List all available ElevenLabs voices
2. **text_to_speech** - Convert text to speech and save as MP3
3. **get_voice_settings** - Get voice-specific settings
4. **check_api_status** - Check ElevenLabs API availability
5. **get_payment_history** - View payment history (FREE)

## Payment Flow

1. User calls a tool through Claude
2. Payment gateway processes $0.10 payment via x402
3. On successful payment, request is forwarded to ElevenLabs server
4. Response includes both the result and payment transaction details

## Development

### Building

```bash
npm run build
```

### Running in Development Mode

```bash
npm run dev
```

## Security Notes

- **NEVER** put private keys with mainnet funds in `.env` files
- Use dedicated development wallets for testing
- The current implementation simulates payments - production implementation would require actual x402 payment server integration

## Extending

To add new tools:
1. Add the tool definition in the TypeScript server
2. Ensure it processes payment before forwarding to Python server
3. Update the Python server if new endpoints are needed

## Troubleshooting

1. **Payment failures**: Check that the user has sufficient balance on the configured network
2. **Connection errors**: Ensure both servers are running and URLs are correct
3. **Tool not found**: Verify the tool name matches between TypeScript and Python servers 