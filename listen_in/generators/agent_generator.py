"""Podcast script generator using OpenAI Agents SDK."""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from agents import Agent, Runner
from pydantic import BaseModel


class PodcastScript(BaseModel):
    """Output schema for podcast script generation."""
    title: str
    """The title of the podcast episode."""
    
    introduction: str
    """The engaging introduction that hooks the listener."""
    
    main_content: str
    """The main body of the podcast script with transitions and markers."""
    
    conclusion: str
    """The memorable conclusion that summarizes key takeaways."""
    
    estimated_duration_minutes: int
    """Estimated speaking duration in minutes."""


class AgentGenerator:
    """Generator for podcast scripts using OpenAI's Agents SDK."""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key."""
        self.api_key = api_key
    
    async def generate(
        self,
        content: Dict[str, Any],
        tone: str = "conversational",
        audience: str = "general",
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Generate a monologue podcast script from parsed content using Agents SDK.
        
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
        
        # Create the agent with gpt-4.1-mini model
        agent = Agent(
            name="PodcastScriptWriter",
            instructions=system_prompt,
            model="o3-2025-04-16",
            output_type=PodcastScript
        )
        
        # Generate the script using Runner
        try:
            # Set API key as environment variable
            os.environ['OPENAI_API_KEY'] = self.api_key
            
            result = await Runner.run(
                agent,
                user_prompt
            )
            
            # Extract the structured output
            script_data = result.final_output
            
            # Format the final script
            script = self._format_script_from_structured(
                script_data,
                metadata,
                tone,
                audience
            )
            
            return script
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate podcast script: {str(e)}")
    
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
8. Make complex topics accessible through analogies and examples

Output a structured podcast script with clear sections."""
    
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
    
    def _format_script_from_structured(
        self, 
        script_data: PodcastScript, 
        metadata: Dict[str, Any],
        tone: str,
        audience: str
    ) -> str:
        """Format the structured output into a markdown script."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_script = f"""# Podcast Script: {script_data.title}

## Metadata
- Source: {metadata.get('filename', 'Unknown')}
- Duration: ~{script_data.estimated_duration_minutes} minutes
- Style: Monologue
- Tone: {tone}
- Audience: {audience}
- Generated: {timestamp}
- Model: OpenAI gpt-4.1-mini (via Agents SDK)

## Script

### Introduction
{script_data.introduction}

### Main Content
{script_data.main_content}

### Conclusion
{script_data.conclusion}

---
*Generated by Listen-in with OpenAI gpt-4.1-mini - Transform documents into engaging podcasts*
"""
        
        return formatted_script