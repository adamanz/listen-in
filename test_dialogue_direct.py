#!/usr/bin/env python3
"""Direct test of the dialogue generator without MCP"""

import asyncio
import os
from dotenv import load_dotenv
from listen_in.generators.dialogue_generator import DialogueGenerator

# Load environment variables
load_dotenv()

async def test_dialogue_generator():
    """Test the dialogue generator directly"""
    
    # Check if API key is set
    api_key = os.getenv("OPEN_AI_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPEN_AI_KEY or OPENAI_API_KEY not set in environment")
        return
    
    print(f"API Key found: {api_key[:10]}...")
    
    # Create generator with API key
    generator = DialogueGenerator(api_key=api_key)
    
    # Test content with proper structure
    raw_content = """Artificial Intelligence safety is becoming increasingly important as AI systems 
become more powerful. Key concerns include alignment (ensuring AI systems do 
what we want), robustness (handling edge cases), and interpretability 
(understanding how AI makes decisions). Researchers are working on various 
approaches including constitutional AI, reward modeling, and mechanistic 
interpretability to address these challenges."""
    
    word_count = len(raw_content.split())
    
    test_content = {
        "content": raw_content,
        "metadata": {
            "filename": "ai_safety.txt",
            "title": "Understanding AI Safety", 
            "word_count": word_count,
            "line_count": 6,
            "file_size": len(raw_content.encode())
        },
        "structure": {
            "sections": [
                {
                    "content": raw_content,
                    "word_count": word_count
                }
            ],
            "has_headings": False,
            "estimated_reading_time": max(1, word_count // 200)
        }
    }
    
    try:
        print("\nGenerating dialogue script...")
        script = await generator.generate(
            content=test_content,
            tone="fun",
            audience="general"
        )
        
        print("\n=== GENERATED DIALOGUE ===")
        print(script)
        print("\n=== END OF DIALOGUE ===")
        
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dialogue_generator())