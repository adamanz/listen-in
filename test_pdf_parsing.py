#!/usr/bin/env python3
"""Test PDF parsing and podcast generation"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from listen_in.parsers.pdf_parser import PDFParser
from listen_in.generators.dialogue_generator import DialogueGenerator
from listen_in.utils.file_utils import save_script

# Load environment variables
load_dotenv()

async def test_pdf_pipeline():
    """Test PDF parsing and dialogue generation"""
    print("🚀 Testing PDF parsing and podcast generation\n")
    
    # Check API key
    openai_key = os.getenv("OPEN_AI_KEY") or os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ ERROR: OpenAI API key not found")
        return
    
    # PDF file path
    pdf_path = "/Users/adamanzuoni/Downloads/CELEX_32016R0679_EN_TXT.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ ERROR: PDF file not found: {pdf_path}")
        return
    
    # Setup output directory
    output_dir = Path("output/pdf_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Parse PDF
        print("📄 Step 1: Parsing PDF document...")
        parser = PDFParser()
        content = parser.parse(pdf_path)
        
        print(f"   ✅ Parsed PDF successfully!")
        print(f"   - Title: {content['metadata'].get('title', 'Unknown')}")
        print(f"   - Pages: {content['metadata']['pages']}")
        print(f"   - Words: {content['metadata']['word_count']}")
        print(f"   - File size: {content['metadata']['file_size'] / 1024 / 1024:.1f} MB")
        
        # Preview content
        preview = content['content'][:500] + "..." if len(content['content']) > 500 else content['content']
        print(f"\n   Content preview:")
        print(f"   {preview}\n")
        
        # Step 2: Generate dialogue script (with reduced content for large PDFs)
        print("🎭 Step 2: Generating dialogue script...")
        
        # For very large documents, use only first portion
        if content['metadata']['word_count'] > 5000:
            print(f"   ⚠️  Document is large ({content['metadata']['word_count']} words), using first 5000 words")
            words = content['content'].split()[:5000]
            content['content'] = ' '.join(words)
            content['metadata']['word_count'] = len(words)
        
        dialogue_gen = DialogueGenerator(api_key=openai_key)
        script = await dialogue_gen.generate(
            content=content,
            tone="informative",
            audience="general",
            custom_instructions="Create an engaging dialogue about GDPR/data protection regulations. Make it accessible and interesting."
        )
        
        # Save script
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = output_dir / f"gdpr_dialogue_{timestamp}.md"
        save_script(script, str(script_path))
        print(f"   ✅ Generated dialogue script: {script_path}")
        
        # Show preview
        lines = script.split('\n')
        dialogue_lines = [line for line in lines if line.strip().startswith('**')][:5]
        print("\n   Dialogue preview:")
        for line in dialogue_lines:
            print(f"   {line}")
        
        print(f"\n✅ PDF test completed successfully!")
        print(f"📁 Output: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_pipeline())