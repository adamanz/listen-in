#!/usr/bin/env python3
"""End-to-end test of dialogue generation pipeline"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from listen_in.parsers.text_parser import TextParser
from listen_in.generators.dialogue_generator import DialogueGenerator
from listen_in.generators.simple_dialogue_audio import SimpleDialogueAudioGenerator
from listen_in.utils.file_utils import save_script

# Load environment variables
load_dotenv()

async def test_pipeline():
    """Run complete end-to-end test"""
    print("🚀 Starting end-to-end dialogue generation test\n")
    
    # Check API keys
    openai_key = os.getenv("OPEN_AI_KEY") or os.getenv("OPENAI_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not openai_key:
        print("❌ ERROR: OpenAI API key not found")
        return
    
    if not elevenlabs_key:
        print("⚠️  WARNING: ElevenLabs API key not found - audio generation will be skipped")
    
    # Setup paths
    test_doc = Path("test_docs/ai_ethics.txt")
    output_dir = Path("output/test_e2e")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Parse document
        print("📄 Step 1: Parsing document...")
        parser = TextParser()
        content = parser.parse(str(test_doc))
        print(f"   ✅ Parsed document: {content['metadata']['word_count']} words")
        
        # Step 2: Generate dialogue script
        print("\n🎭 Step 2: Generating dialogue script...")
        dialogue_gen = DialogueGenerator(api_key=openai_key)
        script = await dialogue_gen.generate(
            content=content,
            tone="fun",
            audience="general",
            custom_instructions="Make it engaging and educational with fun banter between Alex and Sam"
        )
        
        # Save script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = output_dir / f"ai_ethics_dialogue_{timestamp}.md"
        save_script(script, str(script_path))
        print(f"   ✅ Generated dialogue script: {script_path}")
        
        # Show preview
        lines = script.split('\n')
        preview_lines = [line for line in lines if line.strip().startswith('**')][:5]
        print("\n   Preview:")
        for line in preview_lines:
            print(f"   {line}")
        
        # Step 3: Generate audio (if API key available)
        if elevenlabs_key:
            print("\n🎵 Step 3: Generating audio...")
            audio_gen = SimpleDialogueAudioGenerator(api_key=elevenlabs_key)
            
            audio_path = output_dir / f"ai_ethics_dialogue_{timestamp}.mp3"
            audio_result = await audio_gen.generate_audio(
                script_content=script,
                output_path=str(audio_path)
            )
            
            print(f"   ✅ Generated audio: {audio_path}")
            print(f"   Format: {audio_result.get('format', 'unknown')}")
            print(f"   Voice: {audio_result.get('voice_id', 'unknown')}")
        else:
            print("\n⏭️  Step 3: Skipping audio generation (no API key)")
        
        # Step 4: Verify outputs
        print("\n✅ Step 4: Verifying outputs...")
        
        # Check script file
        if script_path.exists():
            script_size = script_path.stat().st_size
            print(f"   ✓ Script file exists: {script_size} bytes")
            
            # Check for dialogue markers
            with open(script_path, 'r') as f:
                script_content = f.read()
                has_alex = "**Alex**:" in script_content
                has_sam = "**Sam**:" in script_content
                print(f"   ✓ Contains Alex dialogue: {has_alex}")
                print(f"   ✓ Contains Sam dialogue: {has_sam}")
        
        # Check audio file if generated
        if elevenlabs_key and 'audio_path' in locals():
            audio_file = Path(audio_path)
            if audio_file.exists():
                audio_size = audio_file.stat().st_size
                print(f"   ✓ Audio file exists: {audio_size} bytes")
        
        print("\n🎉 End-to-end test completed successfully!")
        print(f"\n📁 Output directory: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pipeline())