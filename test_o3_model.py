#!/usr/bin/env python3
"""
Simple test script to validate o3-2025-04-16 OpenAI model is working
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_o3_model():
    """Test the o3-2025-04-16 model with a simple prompt"""
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))
    
    try:
        # Simple test prompt
        response = client.chat.completions.create(
            model="o3-2025-04-16",
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'O3 model is working correctly' to confirm you're functioning."}
            ],
            max_completion_tokens=50,
            temperature=0.1
        )
        
        print("✅ O3 Model Test Results:")
        print(f"Model: {response.model}")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing O3 model: {e}")
        return False

if __name__ == "__main__":
    print("Testing o3-2025-04-16 model...")
    test_o3_model()