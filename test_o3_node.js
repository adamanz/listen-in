#!/usr/bin/env node
/**
 * Simple test script to validate o3-2025-04-16 OpenAI model is working
 */

import OpenAI from "openai";
import dotenv from "dotenv";

// Load environment variables from .env file
dotenv.config();

async function testO3Model() {
    try {
        const client = new OpenAI({
            apiKey: process.env.OPEN_AI_KEY
        });

        const response = await client.responses.create({
            model: "o3-2025-04-16",
            input: "Hello! Please respond with 'O3 model is working correctly' to confirm you're functioning."
        });

        console.log("✅ O3 Model Test Results:");
        console.log(`Model: o3-2025-04-16`);
        console.log(`Response: ${response.output_text}`);
        
        return true;
        
    } catch (error) {
        console.log(`❌ Error testing O3 model: ${error.message}`);
        return false;
    }
}

console.log("Testing o3-2025-04-16 model...");
testO3Model();