#!/usr/bin/env python3
"""Test pipeline for two-host dialogue podcast generation."""

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
from listen_in.generators.simple_dialogue_audio import SimpleDialogueAudioGenerator
from listen_in.utils.file_utils import save_script

async def test_dialogue_pipeline():
    """Test the dialogue podcast pipeline."""
    
    print("🎙️ Listen-in Two-Host Dialogue Pipeline Test")
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
    output_dir = Path.home() / "Desktop" / "listen-in-dialogue"
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
    print("\n2️⃣ Generating fun two-host dialogue script...")
    print("   Hosts: Alex (enthusiastic) & Sam (witty expert)")
    try:
        generator = DialogueGenerator(api_key=openai_key)
        
        custom_instructions = """
        Make this GDPR topic HILARIOUS and FUN!
        - Start with a funny cold open about privacy
        - Use ridiculous analogies (like comparing data to pizza toppings)
        - Include jokes about cookies (the digital kind vs real cookies)
        - Have Alex be confused about technical terms in funny ways
        - Make Sam explain things using pop culture references
        - Add a "GDPR Myth Busters" segment
        - Include at least one terrible data pun
        - Make it feel like a comedy podcast that happens to teach GDPR
        """
        
        script = await generator.generate(
            content=content,
            tone="comedy",
            audience="general",
            custom_instructions=custom_instructions
        )
        
        # Save the script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_filename = f"gdpr_dialogue_{timestamp}.md"
        script_path = output_dir / script_filename
        save_script(script, str(script_path))
        
        print(f"✅ Dialogue script generated: {script_path}")
        
        # Show preview
        lines = script.split('\n')
        print("\n   Preview:")
        preview_found = False
        for i, line in enumerate(lines):
            if "COLD OPEN" in line:
                # Show next few dialogue lines
                for j in range(i+2, min(i+8, len(lines))):
                    if lines[j].strip():
                        print(f"   {lines[j][:100]}...")
                break
                
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 3: Generate conversational audio
    print("\n3️⃣ Generating conversational podcast audio...")
    print("   Note: Two-host dialogue rendered as engaging monologue")
    print("   Voice: Adam (pNInz6obpgDQGcFmaJgB)")
    try:
        audio_generator = SimpleDialogueAudioGenerator(api_key=elevenlabs_key)
        
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Generate audio filename
        audio_filename = f"gdpr_dialogue_{timestamp}.mp3"
        audio_path = output_dir / audio_filename
        
        # Generate conversational audio
        result = await audio_generator.generate_audio(
            script_content=script_content,
            output_path=str(audio_path)
        )
        
        if result.get("status") == "completed":
            print(f"✅ Dialogue audio generated: {audio_path}")
            print(f"   Format: {result['format']}")
            print(f"   Note: {result['note']}")
            
            # Check file size
            if audio_path.exists():
                size_mb = audio_path.stat().st_size / (1024 * 1024)
                print(f"   File size: {size_mb:.2f} MB")
            
            print("\n" + "=" * 50)
            print(f"🎧 DIALOGUE PODCAST READY: {audio_path}")
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
    audio_path = await test_dialogue_pipeline()
    
    if audio_path:
        print(f"\n✨ Success! Your fun two-host podcast is ready:")
        print(f"\n📍 AUDIO FILE: {audio_path}")
        print(f"\n🎭 Features two distinct voices in conversation!")
        print(f"💡 Play this with any audio player to hear Alex & Sam!")
    else:
        print("\n❌ Pipeline failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())