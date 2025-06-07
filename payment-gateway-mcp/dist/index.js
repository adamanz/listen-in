import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import axios from "axios";
import { config } from "dotenv";
import { privateKeyToAccount } from "viem/accounts";
import { withPaymentInterceptor, decodeXPaymentResponse } from "x402-axios";
import { z } from "zod";
// Load environment variables
config();
// Configuration
const USER_PRIVATE_KEY = process.env.USER_PRIVATE_KEY;
const PAYMENT_RECIPIENT = process.env.PAYMENT_RECIPIENT;
const ELEVENLABS_SERVER_URL = process.env.ELEVENLABS_SERVER_URL || "http://localhost:8000";
const PRICE_PER_CALL = process.env.PRICE_PER_CALL || "0.10";
const X402_RESOURCE_SERVER_URL = process.env.X402_RESOURCE_SERVER_URL || "https://x402.org/facilitator";
const X402_NETWORK = process.env.X402_NETWORK || "base-sepolia";
// Validate configuration
if (!USER_PRIVATE_KEY) {
    throw new Error("USER_PRIVATE_KEY is required");
}
if (!PAYMENT_RECIPIENT) {
    throw new Error("PAYMENT_RECIPIENT is required");
}
// Create wallet account from private key
const account = privateKeyToAccount(USER_PRIVATE_KEY);
// Create x402-enabled axios client
const paymentClient = withPaymentInterceptor(axios.create({
    baseURL: X402_RESOURCE_SERVER_URL,
}), account);
// Create regular axios client for ElevenLabs server
const elevenLabsClient = axios.create({
    baseURL: ELEVENLABS_SERVER_URL,
    headers: {
        "Content-Type": "application/json",
    },
});
// Create MCP server
const server = new McpServer({
    name: "ElevenLabs Payment Gateway",
    version: "1.0.0",
});
// Payment state tracking
const paymentLog = [];
// Helper function to process payments
async function processPayment(toolName) {
    try {
        console.error(`Processing payment for tool: ${toolName}`);
        // Make a payment request to the x402 payment server
        const paymentEndpoint = `/pay/${toolName}`;
        const paymentServerUrl = process.env.PAYMENT_SERVER_URL || "http://localhost:4021";
        try {
            // Use the x402-enabled client to make the payment
            const response = await paymentClient.get(`${paymentServerUrl}${paymentEndpoint}`);
            if (response.data.success) {
                // Extract payment response from headers if available
                const paymentResponse = response.headers["x-payment-response"];
                let txHash = response.data.txHash;
                if (paymentResponse) {
                    try {
                        const decoded = decodeXPaymentResponse(paymentResponse);
                        txHash = decoded.transaction || txHash;
                    }
                    catch (e) {
                        console.error("Failed to decode payment response:", e);
                    }
                }
                // Log the payment
                paymentLog.push({
                    timestamp: Date.now(),
                    tool: toolName,
                    amount: PRICE_PER_CALL,
                    txHash,
                });
                console.error(`Payment successful: ${txHash}`);
                return { success: true, txHash };
            }
            else {
                throw new Error("Payment failed");
            }
        }
        catch (error) {
            // If we get a 402 error, it means payment is required but failed
            if (axios.isAxiosError(error) && error.response?.status === 402) {
                const errorMessage = error.response.data?.error || "Payment required";
                throw new Error(errorMessage);
            }
            throw error;
        }
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown payment error";
        console.error(`Payment failed: ${errorMessage}`);
        paymentLog.push({
            timestamp: Date.now(),
            tool: toolName,
            amount: PRICE_PER_CALL,
            error: errorMessage,
        });
        return { success: false, error: errorMessage };
    }
}
// Helper function to call ElevenLabs server
async function callElevenLabsServer(path, params) {
    try {
        const response = await elevenLabsClient.post("/call", {
            method: "tools/call",
            params: {
                name: path,
                arguments: params,
            },
        });
        if (response.data.error) {
            throw new Error(response.data.error.message || "Unknown error from ElevenLabs server");
        }
        return response.data.result;
    }
    catch (error) {
        console.error(`Error calling ElevenLabs server: ${error}`);
        throw error;
    }
}
// Tool: List available voices
server.tool("list_voices", "List all available ElevenLabs voices with their details. Costs $0.10.", {}, async () => {
    // Process payment first
    const payment = await processPayment("list_voices");
    if (!payment.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: `Payment failed: ${payment.error}`,
                        status: "payment_required",
                        amount: PRICE_PER_CALL,
                    }),
                }],
        };
    }
    try {
        // Call the ElevenLabs server
        const result = await callElevenLabsServer("list_voices", {});
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        result,
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
    catch (error) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: error instanceof Error ? error.message : "Unknown error",
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
});
// Tool: Text to speech
server.tool("text_to_speech", "Convert text to speech using ElevenLabs API and save it to a file. Costs $0.10.", {
    text: z.string(),
    voice_id: z.string().optional(),
    output_directory: z.string().optional(),
    model_id: z.string().optional(),
    stability: z.number().optional(),
    similarity_boost: z.number().optional(),
}, async (args) => {
    // Process payment first
    const payment = await processPayment("text_to_speech");
    if (!payment.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: `Payment failed: ${payment.error}`,
                        status: "payment_required",
                        amount: PRICE_PER_CALL,
                    }),
                }],
        };
    }
    try {
        // Debug logging to understand the structure
        console.error(`text_to_speech called with args:`, args);
        console.error(`args keys:`, Object.keys(args || {}));
        // Extract the actual arguments - they should be in args directly
        const actualArgs = {
            text: args.text,
            voice_id: args.voice_id,
            output_directory: args.output_directory,
            model_id: args.model_id,
            stability: args.stability,
            similarity_boost: args.similarity_boost,
        };
        console.error(`Extracted args:`, JSON.stringify(actualArgs));
        // Call the ElevenLabs server with the extracted arguments
        const result = await callElevenLabsServer("text_to_speech", actualArgs);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        result,
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
    catch (error) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: error instanceof Error ? error.message : "Unknown error",
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
});
// Tool: Get voice settings
server.tool("get_voice_settings", "Get the default voice settings for a specific voice. Costs $0.10.", {
    voice_id: z.string(),
}, async (args) => {
    // Process payment first
    const payment = await processPayment("get_voice_settings");
    if (!payment.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: `Payment failed: ${payment.error}`,
                        status: "payment_required",
                        amount: PRICE_PER_CALL,
                    }),
                }],
        };
    }
    try {
        // Call the ElevenLabs server
        const result = await callElevenLabsServer("get_voice_settings", args);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        result,
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
    catch (error) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: error instanceof Error ? error.message : "Unknown error",
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
});
// Tool: Check API status (this one could be free or cheaper)
server.tool("check_api_status", "Check if the ElevenLabs API is configured and accessible. Costs $0.10.", {}, async () => {
    // Process payment first
    const payment = await processPayment("check_api_status");
    if (!payment.success) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: `Payment failed: ${payment.error}`,
                        status: "payment_required",
                        amount: PRICE_PER_CALL,
                    }),
                }],
        };
    }
    try {
        // Call the ElevenLabs server
        const result = await callElevenLabsServer("check_api_status", {});
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        result,
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
    catch (error) {
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        error: error instanceof Error ? error.message : "Unknown error",
                        payment: {
                            amount: PRICE_PER_CALL,
                            txHash: payment.txHash,
                        },
                    }),
                }],
        };
    }
});
// Tool: Get payment history
server.tool("get_payment_history", "Get the payment history for this session. This tool is free.", {}, async () => {
    return {
        content: [{
                type: "text",
                text: JSON.stringify({
                    history: paymentLog,
                    totalSpent: paymentLog
                        .filter((p) => p.txHash)
                        .reduce((sum, p) => sum + parseFloat(p.amount), 0)
                        .toFixed(2),
                }),
            }],
    };
});
// Start the server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Payment Gateway MCP Server started");
    console.error(`Configured to charge $${PRICE_PER_CALL} per tool call`);
    console.error(`Payments will be sent to: ${PAYMENT_RECIPIENT}`);
    console.error(`ElevenLabs server: ${ELEVENLABS_SERVER_URL}`);
}
main().catch((error) => {
    console.error("Failed to start server:", error);
    process.exit(1);
});
