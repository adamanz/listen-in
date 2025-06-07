#!/bin/bash

echo "=== ElevenLabs Payment Gateway Setup ==="
echo

# Check if in correct directory
if [ ! -f "elevenlabs_server.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Step 1: Install Python dependencies
echo "Step 1: Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "Error: Failed to install Python dependencies"
    exit 1
}

# Step 2: Set up TypeScript payment gateway
echo
echo "Step 2: Setting up TypeScript payment gateway..."
cd payment-gateway-mcp || {
    echo "Error: payment-gateway-mcp directory not found"
    exit 1
}

# Install npm dependencies
echo "Installing npm dependencies..."
npm install || {
    echo "Error: Failed to install npm dependencies"
    exit 1
}

# Build TypeScript code
echo "Building TypeScript code..."
npm run build || {
    echo "Error: Failed to build TypeScript code"
    exit 1
}

# Step 3: Create example .env file
if [ ! -f ".env" ]; then
    echo
    echo "Step 3: Creating example .env file..."
    cat > .env.example << EOF
# User's private key for making payments (NEVER use mainnet funds!)
USER_PRIVATE_KEY=0x...

# Your wallet address to receive payments
PAYMENT_RECIPIENT=0x...

# ElevenLabs server configuration
ELEVENLABS_SERVER_URL=http://localhost:8000
HTTP_PORT=8000

# Payment configuration
PRICE_PER_CALL=0.10
PAYMENT_SERVER_URL=http://localhost:4021
PAYMENT_SERVER_PORT=4021

# x402 configuration
X402_NETWORK=base-sepolia
X402_RESOURCE_SERVER_URL=https://x402.org/facilitator
EOF
    echo "Created .env.example - please copy to .env and configure"
fi

cd ..

# Step 4: Create run scripts
echo
echo "Step 4: Creating run scripts..."

# Create script to run all servers
cat > run-all.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting ElevenLabs Payment Gateway System${NC}"
echo

# Check for .env file
if [ ! -f "payment-gateway-mcp/.env" ]; then
    echo -e "${RED}Error: payment-gateway-mcp/.env not found${NC}"
    echo "Please copy payment-gateway-mcp/.env.example to payment-gateway-mcp/.env and configure it"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down all servers...${NC}"
    kill $PYTHON_PID $PAYMENT_PID $GATEWAY_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start Python ElevenLabs HTTP server
echo -e "${GREEN}Starting ElevenLabs HTTP server on port 8000...${NC}"
python elevenlabs_server.py --http &
PYTHON_PID=$!
sleep 2

# Start x402 payment server
echo -e "${GREEN}Starting x402 payment server on port 4021...${NC}"
cd payment-gateway-mcp
npm run payment-server &
PAYMENT_PID=$!
cd ..
sleep 2

# Start MCP payment gateway
echo -e "${GREEN}Starting MCP payment gateway...${NC}"
cd payment-gateway-mcp
npm run dev &
GATEWAY_PID=$!
cd ..

echo
echo -e "${GREEN}All servers started!${NC}"
echo
echo "Servers running:"
echo "- ElevenLabs HTTP server: http://localhost:8000"
echo "- x402 Payment server: http://localhost:4021"
echo "- MCP Payment Gateway: Running in stdio mode"
echo
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for any process to exit
wait
EOF

chmod +x run-all.sh

# Create test script
cat > test-payment-gateway.sh << 'EOF'
#!/bin/bash

echo "Testing Payment Gateway Integration"
echo

# Test the ElevenLabs HTTP server
echo "1. Testing ElevenLabs HTTP server..."
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "check_api_status",
      "arguments": {}
    }
  }' | jq .

echo
echo "2. Testing x402 payment server..."
echo "Note: This will return 402 Payment Required if no payment header is sent"
curl -v http://localhost:4021/pay/test_tool

echo
echo "Test complete!"
EOF

chmod +x test-payment-gateway.sh

echo
echo "=== Setup Complete! ==="
echo
echo "Next steps:"
echo "1. Copy payment-gateway-mcp/.env.example to payment-gateway-mcp/.env"
echo "2. Configure your environment variables:"
echo "   - USER_PRIVATE_KEY: Private key for payment wallet"
echo "   - PAYMENT_RECIPIENT: Your wallet address to receive payments"
echo "   - ELEVENLABS_API_KEY: Your ElevenLabs API key (in main .env)"
echo
echo "3. Run all servers with: ./run-all.sh"
echo "4. Test the setup with: ./test-payment-gateway.sh"
echo
echo "5. Configure Claude Desktop to use the payment gateway" 