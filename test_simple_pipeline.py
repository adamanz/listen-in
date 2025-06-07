#!/usr/bin/env python3
"""Simple end-to-end test without FastMCP wrapper."""

import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components directly
from listen_in.parsers.text_parser import TextParser
from listen_in.generators.monologue_generator import MonologueGenerator
from listen_in.generators.simple_audio_generator import SimpleAudioGenerator
from listen_in.utils.file_utils import save_script

async def test_simple_pipeline():
    """Test the complete pipeline without MCP wrapper."""
    
    print("🎙️ Listen-in Simple End-to-End Test")
    print("=" * 50)
    
    # Get API keys from environment
    openai_key = os.environ.get("OPEN_AI_KEY")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    
    if not openai_key:
        print("❌ OpenAI API key not found in .env (OPEN_AI_KEY)")
        return None
    if not elevenlabs_key:
        print("❌ ElevenLabs API key not found in .env (ELEVENLABS_API_KEY)")
        return None
    
    print("✅ API keys loaded from .env")
    
    # Set up paths
    input_file = "/Users/adamanzuoni/listen-in/examples/gdpr_excerpt_test.txt"
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Parse the text file
    print("\n1️⃣ Parsing text file...")
    try:
        parser = TextParser()
        content = parser.parse(input_file)
        print(f"✅ Parsed {content['metadata']['word_count']} words")
        print(f"   Title: {content['metadata']['title']}")
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return None
    
    # Step 2: Generate podcast script
    print("\n2️⃣ Generating podcast script with o3-2025-04-16...")
    try:
        generator = MonologueGenerator(api_key=openai_key)
        
        custom_instructions = """
        Create an engaging 3-5 minute podcast about GDPR.
        Make it accessible and interesting for a general audience.
        Use analogies and real-world examples.
        Focus on why data privacy matters to everyday people.
        """
        
        script = await generator.generate(
            content=content,
            tone="conversational",
            audience="general",
            custom_instructions=custom_instructions
        )
        
        # Save the script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"gdpr_podcast_simple_{timestamp}.md"
        script_path = output_dir / script_filename
        save_script(script, str(script_path))
        
        print(f"✅ Script generated: {script_path}")
        
        # Show preview
        lines = script.split('\n')
        print("\n   Preview:")
        for line in lines[15:20]:  # Show a few lines
            if line.strip():
                print(f"   {line[:80]}...")
                
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 3: Generate audio
    print("\n3️⃣ Generating audio with ElevenLabs...")
    try:
        audio_generator = SimpleAudioGenerator(api_key=elevenlabs_key)
        
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Generate audio filename
        audio_filename = f"gdpr_podcast_simple_{timestamp}.mp3"
        audio_path = output_dir / audio_filename
        
        # Generate audio
        result = await audio_generator.generate_audio(
            script_content=script_content,
            output_path=str(audio_path),
            voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        )
        
        if result.get("status") == "completed":
            print(f"✅ Audio generated: {audio_path}")
            print(f"   Voice ID: {result['voice_id']}")
            print(f"   Model: {result['model_id']}")
            
            # Check file size
            if audio_path.exists():
                size_mb = audio_path.stat().st_size / (1024 * 1024)
                print(f"   File size: {size_mb:.2f} MB")
            
            print("\n" + "=" * 50)
            print(f"🎧 AUDIO FILE PATH: {audio_path}")
            print("=" * 50)
            
            return str(audio_path)
        else:
            print(f"⏳ Audio generation in progress...")
            return None
            
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run the test and output the audio file path."""
    audio_path = await test_simple_pipeline()
    
    if audio_path:
        print(f"\n✨ Success! Your podcast is ready:")
        print(f"\n📍 AUDIO FILE: {audio_path}")
        print(f"\n💡 You can play this file with any audio player!")
    else:
        print("\n❌ Pipeline failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())