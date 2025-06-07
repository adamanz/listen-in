import express from "express";
import { config } from "dotenv";
import { paymentMiddleware } from "x402-express";
config();
const payTo = process.env.PAYMENT_RECIPIENT;
const network = (process.env.X402_NETWORK || "base-sepolia");
const port = process.env.PAYMENT_SERVER_PORT || 4021;
if (!payTo) {
    console.error("PAYMENT_RECIPIENT is required");
    process.exit(1);
}
const app = express();
// Configure x402 payment middleware for each tool endpoint
app.use(paymentMiddleware(payTo, {
    "/pay/list_voices": {
        price: "$0.10",
        network,
    },
    "/pay/text_to_speech": {
        price: "$0.10",
        network,
    },
    "/pay/get_voice_settings": {
        price: "$0.10",
        network,
    },
    "/pay/check_api_status": {
        price: "$0.10",
        network,
    },
}, {
    url: "https://x402.org/facilitator",
}));
// Payment endpoints - return success after payment is verified
app.get("/pay/:tool", (req, res) => {
    const tool = req.params.tool;
    res.json({
        success: true,
        tool,
        amount: "0.10",
        txHash: res.locals.paymentTxHash || "simulated",
        timestamp: Date.now(),
    });
});
app.post("/pay/:tool", (req, res) => {
    const tool = req.params.tool;
    res.json({
        success: true,
        tool,
        amount: "0.10",
        txHash: res.locals.paymentTxHash || "simulated",
        timestamp: Date.now(),
    });
});
app.listen(port, () => {
    console.log(`x402 Payment Server listening at http://localhost:${port}`);
    console.log(`Payments will be sent to: ${payTo}`);
    console.log(`Network: ${network}`);
});
