#!/usr/bin/env python3
"""Test 2-person dialogue podcast generation - 5 minutes long."""

import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components directly
from listen_in.parsers.text_parser import TextParser
from listen_in.generators.dialogue_generator import DialogueGenerator
from listen_in.generators.simple_audio_generator import SimpleAudioGenerator
from listen_in.utils.file_utils import save_script

async def test_dialogue_podcast():
    """Test 2-person dialogue podcast generation."""
    
    print("🎙️ Listen-in 2-Person Dialogue Test (5 minutes)")
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
    
    # Step 2: Generate dialogue podcast script
    print("\n2️⃣ Generating 2-person dialogue script with o3-2025-04-16...")
    print("   Hosts: Alex (enthusiastic) & Sam (witty expert)")
    try:
        generator = DialogueGenerator(api_key=openai_key)
        
        custom_instructions = """
        Create an ENTERTAINING 5-minute dialogue podcast about GDPR between Alex and Sam.
        
        TARGET: Exactly 5 minutes of speaking time (750-800 words of dialogue)
        
        Make it FUN and ACCESSIBLE:
        - Alex should be curious and excited about learning
        - Sam should explain things with clever analogies and humor
        - Include at least 3 funny moments or jokes
        - Use pop culture references and relatable examples
        - Make GDPR feel relevant to everyday people
        - Include reactions like "No way!", "Wait, what?", "That's wild!"
        
        Structure for 5 minutes:
        - Cold open (30 seconds) - Hook with a funny GDPR scenario
        - Introduction (1 minute) - Set up the topic with enthusiasm
        - Main discussion (3 minutes) - Break down GDPR with humor and examples
        - Fun facts segment (30 seconds) - Quick lightning round
        - Conclusion (1 minute) - Memorable wrap-up and sign-off
        """
        
        script = await generator.generate(
            content=content,
            tone="fun",
            audience="general",
            custom_instructions=custom_instructions
        )
        
        # Save the script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"gdpr_dialogue_5min_{timestamp}.md"
        script_path = output_dir / script_filename
        save_script(script, str(script_path))
        
        print(f"✅ Dialogue script generated: {script_path}")
        
        # Show preview
        lines = script.split('\n')
        preview_lines = []
        for line in lines:
            if "**Alex**:" in line or "**Sam**:" in line:
                preview_lines.append(line[:100])
                if len(preview_lines) >= 6:
                    break
        
        print("\n   Dialogue Preview:")
        for line in preview_lines:
            print(f"   {line}...")
                
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 3: Generate audio with conversation mode
    print("\n3️⃣ Generating audio with ElevenLabs (conversation mode)...")
    try:
        audio_generator = SimpleAudioGenerator(api_key=elevenlabs_key)
        
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Generate audio filename
        audio_filename = f"gdpr_dialogue_5min_{timestamp}.mp3"
        audio_path = output_dir / audio_filename
        
        # Generate audio (SimpleAudioGenerator uses TTS, not conversation mode)
        result = await audio_generator.generate_audio(
            script_content=script_content,
            output_path=str(audio_path),
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            output_format="mp3_44100_192"  # High quality with upgraded subscription
        )
        
        if result.get("status") == "completed":
            print(f"✅ Audio generated: {audio_path}")
            print(f"   Mode: {result.get('voice_mode', 'conversation')}")
            print(f"   Quality: {result.get('quality', 'high')}")
            
            # Check file size
            if audio_path.exists():
                size_mb = audio_path.stat().st_size / (1024 * 1024)
                duration_estimate = size_mb * 8  # Rough estimate: 1MB ≈ 8 minutes
                print(f"   File size: {size_mb:.2f} MB")
                print(f"   Estimated duration: ~{duration_estimate:.1f} minutes")
            
            print("\n" + "=" * 60)
            print(f"🎧 2-PERSON DIALOGUE PODCAST READY!")
            print(f"📍 {audio_path}")
            print("🎭 Featuring Alex (enthusiastic) & Sam (expert)")
            print("⏱️  Target: 5 minutes of entertaining GDPR discussion")
            print("=" * 60)
            
            return str(audio_path)
        else:
            print(f"⏳ Audio generation status: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run the dialogue test."""
    audio_path = await test_dialogue_podcast()
    
    if audio_path:
        print(f"\n✨ Success! Your 2-person dialogue podcast is ready:")
        print(f"\n📍 AUDIO FILE: {audio_path}")
        print(f"\n🎉 Enjoy your fun GDPR dialogue with Alex & Sam!")
    else:
        print("\n❌ Dialogue generation failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())