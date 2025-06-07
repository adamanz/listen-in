#!/usr/bin/env python3
"""Test podcast generation with GDPR document."""

import asyncio
import sys
import os
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent))

from listen_in.server import (
    configure, 
    generate_podcast_script,
    generate_podcast_audio,
    list_available_voices
)

async def test_podcast_generation():
    """Test the full podcast generation pipeline."""
    
    print("🎙️ Listen-in Podcast Generation Test")
    print("=" * 50)
    
    # Step 1: Configure (will use .env automatically)
    print("\n1. Configuring server...")
    try:
        config_result = await configure()
        print(f"✅ {config_result}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Step 2: List available voices
    print("\n2. Available voices:")
    try:
        voices = await list_available_voices()
        print("Preset voices:")
        for name, info in voices["preset_voices"].items():
            print(f"  - {name}: {info['voice_id'][:8]}...")
    except Exception as e:
        print(f"❌ Error listing voices: {e}")
    
    # Step 3: Generate podcast script
    print("\n3. Generating podcast script from GDPR excerpt...")
    try:
        script_result = await generate_podcast_script(
            file_path="/Users/adamanzuoni/listen-in/examples/gdpr_excerpt_test.txt",
            style="monologue",
            tone="conversational",
            audience="general",
            custom_instructions="""
            Make this legal document engaging and accessible. 
            Use analogies to explain complex concepts. 
            Focus on why GDPR matters to everyday people.
            Keep it under 5 minutes of speaking time.
            """
        )
        print(f"✅ Script generated: {script_result['script_path']}")
        print(f"   Style: {script_result['style']}")
        print(f"   Tone: {script_result['tone']}")
        print(f"   Generated at: {script_result['generated_at']}")
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        return
    
    # Step 4: Generate audio (if ElevenLabs is configured)
    print("\n4. Generating audio from script...")
    try:
        audio_result = await generate_podcast_audio(
            script_path=script_result['script_path'],
            voice_name="rachel",  # Using Rachel voice
            quality="standard",
            duration_scale="default"
        )
        
        if audio_result.get("status") == "completed":
            print(f"✅ Audio generated: {audio_result['audio_path']}")
            print(f"   Quality: {audio_result['quality']}")
            print(f"   Duration scale: {audio_result['duration_scale']}")
        else:
            print(f"⏳ Audio generation in progress: {audio_result}")
            
    except ValueError as e:
        if "ElevenLabs API key not configured" in str(e):
            print("ℹ️  Audio generation skipped (no ElevenLabs API key)")
        else:
            print(f"❌ Audio generation error: {e}")
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
    
    # Return paths for reference
    return {
        "script_path": script_result.get('script_path'),
        "audio_path": audio_result.get('audio_path') if 'audio_result' in locals() else None
    }

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_podcast_generation())
    
    if result['script_path']:
        print(f"\n📄 Script saved at: {result['script_path']}")
    if result['audio_path']:
        print(f"🔊 Audio saved at: {result['audio_path']}")