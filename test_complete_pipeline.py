#!/usr/bin/env python3
"""Test complete pipeline: PDF -> Text -> Script -> Audio"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from listen_in.server import (
    configure, 
    generate_podcast_script,
    generate_podcast_audio,
    list_available_voices
)
from listen_in.config import OPENAI_API_KEY, ELEVENLABS_API_KEY

async def test_complete_pipeline():
    """Test the complete pipeline and return audio file path."""
    
    print("🎙️ Listen-in Complete Pipeline Test")
    print("=" * 50)
    
    # Check if we already have the text file
    text_file = Path("/Users/adamanzuoni/listen-in/examples/gdpr_excerpt_test.txt")
    if not text_file.exists():
        print("❌ Text file not found. Please convert PDF first.")
        return None
    
    # Step 1: Configure (will use .env automatically)
    print("\n1️⃣ Configuring server...")
    try:
        if not OPENAI_API_KEY:
            print("❌ OpenAI API key not found in .env")
            return None
        if not ELEVENLABS_API_KEY:
            print("❌ ElevenLabs API key not found in .env")
            return None
            
        config_result = await configure()
        print(f"✅ {config_result}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return None
    
    # Step 2: Generate podcast script
    print("\n2️⃣ Generating podcast script...")
    try:
        script_result = await generate_podcast_script(
            file_path=str(text_file),
            style="monologue",
            tone="conversational",
            audience="general",
            custom_instructions="""
            Create an engaging 3-5 minute podcast about GDPR.
            Make it accessible and interesting for a general audience.
            Use analogies and real-world examples.
            Focus on why data privacy matters to everyday people.
            """
        )
        script_path = script_result['script_path']
        print(f"✅ Script generated: {script_path}")
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        return None
    
    # Step 3: Generate audio
    print("\n3️⃣ Generating audio...")
    try:
        audio_result = await generate_podcast_audio(
            script_path=script_path,
            voice_name="rachel",  # Professional female voice
            quality="standard",
            duration_scale="default"
        )
        
        if audio_result.get("status") == "completed":
            audio_path = audio_result['audio_path']
            print(f"✅ Audio generated: {audio_path}")
            print("\n" + "=" * 50)
            print(f"🎧 AUDIO FILE PATH: {audio_path}")
            print("=" * 50)
            return audio_path
        else:
            print(f"⏳ Audio generation status: {audio_result}")
            return None
            
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
        return None

async def main():
    """Run the test and output the audio file path."""
    audio_path = await test_complete_pipeline()
    
    if audio_path:
        print(f"\n✨ Success! Your podcast audio is ready:")
        print(f"📍 {audio_path}")
        
        # Also print the directory for easy access
        audio_dir = Path(audio_path).parent
        print(f"\n📂 Open this folder to find your audio file:")
        print(f"   {audio_dir}")
    else:
        print("\n❌ Pipeline failed. Check the errors above.")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())