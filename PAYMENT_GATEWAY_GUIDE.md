# ElevenLabs x402 Payment Gateway Guide

This guide explains how to integrate x402 payments with your ElevenLabs MCP server, allowing you to charge users 10 cents per tool call.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────────┐     ┌────────────────────┐     ┌─────────────────┐
│ Claude Desktop  │────▶│ Payment Gateway MCP │────▶│ x402 Payment Server│────▶│ ElevenLabs HTTP │
│                 │     │   (TypeScript)      │     │   (TypeScript)     │     │    (Python)     │
└─────────────────┘     └─────────────────────┘     └────────────────────┘     └─────────────────┘
                               │                              │
                               │ Processes payments          │ Verifies & settles
                               │ via x402 protocol           │ on blockchain
                               ▼                              ▼
                        User's Wallet                   Your Wallet
```

## Prerequisites

- Node.js v20+ and npm
- Python 3.8+
- A wallet with USDC on Base Sepolia (for testing)
- ElevenLabs API key

## Quick Setup

1. **Run the setup script:**
   ```bash
   chmod +x setup-payment-gateway.sh
   ./setup-payment-gateway.sh
   ```

2. **Configure environment variables:**
   Copy and edit the .env files:
   ```bash
   # For the payment gateway
   cp payment-gateway-mcp/.env.example payment-gateway-mcp/.env
   # Edit with your wallet details
   ```

3. **Start all servers:**
   ```bash
   ./run-all.sh
   ```

## Detailed Setup Guide

### Step 1: Generate a Development Wallet

**Never use a wallet with mainnet funds for development!**

Using Foundry (recommended):
```bash
# Install foundry if not already installed
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Generate a new wallet
cast wallet new
```

Save the private key and address. You'll need:
- Private key: For USER_PRIVATE_KEY (user's payment wallet)
- Address: To fund with test USDC

### Step 2: Fund Your Wallet

Get test USDC on Base Sepolia:
1. Visit [CDP Faucet](https://portal.cdp.coinbase.com/products/faucet)
2. Select "Base Sepolia" network
3. Enter your wallet address
4. Request test funds

### Step 3: Configure Environment Variables

Edit `payment-gateway-mcp/.env`:
```env
# User's private key (from Step 1)
USER_PRIVATE_KEY=0x...your_private_key...

# Your wallet address to receive payments
PAYMENT_RECIPIENT=0x...your_receiving_address...

# Server configuration
ELEVENLABS_SERVER_URL=http://localhost:8000
PRICE_PER_CALL=0.10

# x402 configuration
X402_NETWORK=base-sepolia
PAYMENT_SERVER_URL=http://localhost:4021
```

### Step 4: Configure Claude Desktop

Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "elevenlabs-paid": {
      "command": "node",
      "args": ["/absolute/path/to/payment-gateway-mcp/dist/index.js"],
      "env": {
        "USER_PRIVATE_KEY": "0x...user_private_key...",
        "PAYMENT_RECIPIENT": "0x...your_address...",
        "ELEVENLABS_SERVER_URL": "http://localhost:8000",
        "PRICE_PER_CALL": "0.10"
      }
    }
  }
}
```

## How It Works

### Payment Flow

1. **User requests a tool** (e.g., text_to_speech) through Claude
2. **Payment Gateway intercepts** the request
3. **x402 payment is processed:**
   - Gateway creates payment request for $0.10
   - User's wallet signs the payment
   - Payment is sent to x402 server
   - x402 server verifies and settles on blockchain
4. **On successful payment:**
   - Request is forwarded to ElevenLabs server
   - TTS is generated and saved
   - Response includes result + payment receipt
5. **On failed payment:**
   - Error is returned to user
   - No ElevenLabs API call is made

### Available Tools

All tools cost $0.10 per call:
- `list_voices` - List available ElevenLabs voices
- `text_to_speech` - Convert text to speech
- `get_voice_settings` - Get voice settings
- `check_api_status` - Check API status
- `get_payment_history` - View payments (FREE)

### Example Usage in Claude

```
User: "Convert this text to speech: Hello world!"
Claude: [Processes $0.10 payment, then generates audio]
Response: Audio saved to ~/Desktop/tts_1234567890.mp3
Payment: $0.10 (tx: 0xabc123...)
```

## Testing

### Test the Integration

Run the test script:
```bash
./test-payment-gateway.sh
```

### Manual Testing

1. **Test ElevenLabs HTTP server:**
   ```bash
   curl -X POST http://localhost:8000/call \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "check_api_status",
         "arguments": {}
       }
     }'
   ```

2. **Test payment server (will return 402):**
   ```bash
   curl http://localhost:4021/pay/test_tool
   ```

## Production Deployment

### Using Base Mainnet

For production with real USDC on Base mainnet:

1. **Update configuration:**
   ```env
   X402_NETWORK=base
   X402_RESOURCE_SERVER_URL=https://x402.org/facilitator
   ```

2. **Get CDP API keys:**
   - Visit [Coinbase Developer Platform](https://portal.cdp.coinbase.com/)
   - Create API keys
   - Add to environment:
     ```env
     CDP_API_KEY_ID=your_key_id
     CDP_API_KEY_SECRET=your_key_secret
     ```

3. **Use production wallets:**
   - Create dedicated production wallets
   - Fund with real USDC on Base mainnet
   - Implement proper key management

### Security Best Practices

1. **Private Key Management:**
   - Never commit private keys to version control
   - Use environment variables or secure key management services
   - Rotate keys regularly

2. **Access Control:**
   - Implement authentication for the payment gateway
   - Rate limit API calls
   - Monitor for suspicious activity

3. **Payment Validation:**
   - Verify payment amounts match expected prices
   - Implement refund mechanisms if needed
   - Log all transactions for auditing

## Troubleshooting

### Common Issues

1. **"Payment failed" errors:**
   - Check wallet has sufficient USDC balance
   - Verify correct network (Base Sepolia for testing)
   - Ensure private key is correctly formatted

2. **"Tool not found" errors:**
   - Verify all servers are running
   - Check server URLs in configuration
   - Ensure Python server is running with `--http` flag

3. **Connection errors:**
   - Check firewall settings
   - Verify ports 8000 and 4021 are available
   - Restart all servers

### Debug Mode

Enable debug logging:
```bash
# In payment-gateway-mcp/.env
DEBUG=true
```

View payment history:
```
User: "Show me my payment history"
Claude: [Calls get_payment_history tool - FREE]
```

## Advanced Configuration

### Custom Pricing

Modify prices per tool in `src/x402-payment-server.ts`:
```typescript
"/pay/text_to_speech": {
  price: "$0.25",  // Premium pricing for TTS
  network,
},
"/pay/list_voices": {
  price: "$0.05",   // Cheaper for listings
  network,
},
```

### Adding New Tools

1. Add to TypeScript payment gateway (`src/index.ts`)
2. Add to x402 payment server (`src/x402-payment-server.ts`)
3. Implement in Python server if needed
4. Update documentation

### Webhook Integration

For post-payment actions:
```typescript
// In processPayment function
if (payment.success) {
  await notifyWebhook({
    tool: toolName,
    txHash: payment.txHash,
    amount: PRICE_PER_CALL,
    timestamp: Date.now(),
  });
}
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs
3. Verify wallet configuration
4. Test with small amounts first

## License

This integration is provided as-is for educational and development purposes. Please review the x402 protocol documentation and terms of service before production use.