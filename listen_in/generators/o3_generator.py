"""O3 model-based podcast script generator using Agents API."""

from typing import Dict, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI


class O3Generator:
    """Generator for podcast scripts using OpenAI's o3 model via Agents API."""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key."""
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate(
        self,
        content: Dict[str, Any],
        tone: str = "conversational",
        audience: str = "general",
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Generate a monologue podcast script from parsed content using o3.
        
        Args:
            content: Parsed document content with metadata
            tone: Tone of the script (conversational, educational, etc.)
            audience: Target audience level
            custom_instructions: Additional generation instructions
            
        Returns:
            Generated podcast script in markdown format
        """
        # Extract document info
        doc_content = content["content"]
        metadata = content["metadata"]
        structure = content["structure"]
        
        # Build the system prompt
        system_prompt = self._build_system_prompt(tone, audience)
        
        # Build the user prompt
        user_prompt = self._build_user_prompt(
            doc_content, 
            metadata, 
            structure,
            custom_instructions
        )
        
        # Generate the script using o3
        try:
            # Combine system and user prompts for o3 model
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = await self.client.responses.create(
                model="o3-2025-04-16",
                input=combined_prompt
            )
            
            # Format the final script
            script = self._format_script(
                response.output_text,
                metadata,
                tone,
                audience
            )
            
            return script
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate podcast script with o3: {str(e)}")
    
    def _build_system_prompt(self, tone: str, audience: str) -> str:
        """Build the system prompt for the LLM."""
        tone_guides = {
            "conversational": "friendly, engaging, and natural as if talking to a friend",
            "educational": "clear, informative, and structured for learning",
            "professional": "polished, authoritative, and business-appropriate",
            "casual": "relaxed, informal, and entertaining"
        }
        
        audience_guides = {
            "general": "accessible to anyone with basic knowledge",
            "beginner": "simple explanations, avoid jargon, define terms",
            "expert": "technical depth is welcome, assume domain knowledge",
            "young": "energetic, relatable examples, shorter sentences"
        }
        
        tone_guide = tone_guides.get(tone, tone_guides["conversational"])
        audience_guide = audience_guides.get(audience, audience_guides["general"])
        
        return f"""You are a professional podcast script writer. Your task is to transform written documents into engaging monologue podcast scripts.

Key guidelines:
1. Write in a {tone_guide} style
2. Target audience: {audience_guide}
3. Create natural speech patterns with:
   - Conversational transitions
   - Rhetorical questions
   - Personal connections ("you might wonder...", "imagine this...")
   - Natural pauses marked with [PAUSE]
   - Emphasis markers [EMPHASIS] for important points
4. Structure with:
   - Engaging hook/introduction
   - Clear topic transitions
   - Memorable conclusion
5. Keep sentences short and punchy for audio
6. Use active voice
7. Include time estimates for sections
8. Make complex topics accessible through analogies and examples"""
    
    def _build_user_prompt(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        structure: Dict[str, Any],
        custom_instructions: Optional[str]
    ) -> str:
        """Build the user prompt with document content."""
        # For large documents, create a summary first
        word_count = metadata.get('word_count', 0)
        
        # If document is very large, truncate intelligently
        if word_count > 3000:
            # Take beginning, middle, and end sections
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Take first 30%, middle 40%, last 30%
            first_section = '\n'.join(lines[:int(total_lines * 0.3)])
            middle_start = int(total_lines * 0.3)
            middle_end = int(total_lines * 0.7)
            middle_section = '\n'.join(lines[middle_start:middle_end])
            last_section = '\n'.join(lines[int(total_lines * 0.7):])
            
            content = f"{first_section}\n\n[... content truncated ...]\n\n{middle_section}\n\n[... content truncated ...]\n\n{last_section}"
            
        prompt = f"""Transform this document into an engaging podcast monologue script.

Document Title: {metadata.get('title', 'Untitled')}
Word Count: {metadata.get('word_count', 0)}
Estimated Speaking Time: {metadata.get('word_count', 0) // 150} minutes

Document Content:
---
{content}
---

Requirements:
1. Create a natural, flowing monologue that sounds great when read aloud
2. Add an engaging introduction that hooks the listener
3. Include smooth transitions between topics
4. Add [PAUSE] markers for natural breathing points
5. Use [EMPHASIS] for key points that need vocal emphasis
6. End with a memorable conclusion that summarizes key takeaways
7. Maintain accuracy to the source material while making it conversational
"""
        
        if custom_instructions:
            prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"
        
        return prompt
    
    def _format_script(
        self, 
        raw_script: str, 
        metadata: Dict[str, Any],
        tone: str,
        audience: str
    ) -> str:
        """Format the generated script with metadata."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_script = f"""# Podcast Script: {metadata.get('title', 'Untitled')}

## Metadata
- Source: {metadata.get('filename', 'Unknown')}
- Duration: ~{metadata.get('word_count', 0) // 150} minutes
- Style: Monologue
- Tone: {tone}
- Audience: {audience}
- Generated: {timestamp}
- Model: OpenAI o3

## Script

{raw_script}

---
*Generated by Listen-in with OpenAI o3 - Transform documents into engaging podcasts*
"""
        
        return formatted_script