"""Dialogue-style podcast script generator with two hosts using OpenAI Agents SDK."""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from agents import Agent, Runner
from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    """A single line of dialogue in the podcast."""
    speaker: str = Field(description="Either 'Alex' or 'Sam'")
    text: str = Field(description="What the speaker says")
    tone: Optional[str] = Field(default=None, description="Optional tone indicator like 'laughing', 'excited', 'thoughtful'")


class PodcastDialogue(BaseModel):
    """Output schema for two-host podcast script generation."""
    title: str
    """The catchy title of the podcast episode."""
    
    cold_open: list[DialogueLine]
    """The fun opening banter before introducing the topic."""
    
    introduction: list[DialogueLine]
    """The introduction where hosts set up the topic."""
    
    main_content: list[DialogueLine]
    """The main discussion with back-and-forth dialogue."""
    
    fun_facts_segment: list[DialogueLine]
    """A fun segment with interesting facts or analogies."""
    
    conclusion: list[DialogueLine]
    """The wrap-up with key takeaways and sign-off."""
    
    estimated_duration_minutes: int
    """Estimated speaking duration in minutes."""


class DialogueGenerator:
    """Generator for two-host dialogue podcast scripts using OpenAI's Agents SDK."""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key."""
        self.api_key = api_key
    
    async def generate(
        self,
        content: Dict[str, Any],
        tone: str = "fun",
        audience: str = "general",
        duration_minutes: int = 5,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Generate a two-host dialogue podcast script from parsed content.
        
        Args:
            content: Parsed document content with metadata
            tone: Tone of the script (fun, educational, comedy, etc.)
            audience: Target audience level
            duration_minutes: Target duration in minutes (default: 5)
            custom_instructions: Additional generation instructions
            
        Returns:
            Generated podcast script in markdown format
        """
        # Extract document info
        doc_content = content["content"]
        metadata = content["metadata"]
        structure = content["structure"]
        
        # Build the system prompt
        system_prompt = self._build_system_prompt(tone, audience, duration_minutes)
        
        # Build the user prompt
        user_prompt = self._build_user_prompt(
            doc_content, 
            metadata, 
            structure,
            duration_minutes,
            custom_instructions
        )
        
        # Create the agent with gpt-4.1-mini model
        agent = Agent(
            name="PodcastDialogueWriter",
            instructions=system_prompt,
            model="o3-2025-04-16",
            output_type=PodcastDialogue
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
            dialogue_data = result.final_output
            
            # Format the final script
            script = self._format_dialogue_script(
                dialogue_data,
                metadata,
                tone,
                audience
            )
            
            return script
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate dialogue script: {str(e)}")
    
    def _build_system_prompt(self, tone: str, audience: str, duration_minutes: int) -> str:
        """Build the system prompt for the LLM."""
        tone_guides = {
            "fun": "playful, energetic, with jokes and wordplay",
            "comedy": "hilarious, full of puns and comedic timing",
            "educational": "informative but entertaining, like edutainment",
            "casual": "relaxed, like friends chatting over coffee"
        }
        
        audience_guides = {
            "general": "accessible to anyone, explain complex topics simply",
            "beginner": "extra simple, lots of analogies and examples",
            "expert": "can use technical terms but keep it entertaining",
            "young": "high energy, pop culture references, memes"
        }
        
        tone_guide = tone_guides.get(tone, tone_guides["fun"])
        audience_guide = audience_guides.get(audience, audience_guides["general"])
        
        return f"""You are a professional podcast script writer creating a dialogue between two hosts:

HOST PERSONALITIES:
- ALEX: The enthusiastic one. Curious, asks great questions, makes pop culture references, slightly nerdy but charming. Uses phrases like "Wait, wait, wait!" and "Okay, but here's the wild part..."
- SAM: The witty expert. More knowledgeable but explains things simply, loves analogies, occasionally sarcastic but warm. Uses phrases like "So here's the thing..." and "Picture this..."

STYLE GUIDELINES:
1. Write in a {tone_guide} style
2. Target audience: {audience_guide}
3. Create natural banter with:
   - Interruptions and reactions ("No way!", "Hold up!")
   - Inside jokes that develop during the episode
   - Playful teasing between hosts
   - Sound effects in brackets like [ALEX laughs], [SAM gasps]
   - Natural speech patterns (contractions, incomplete sentences)
4. Structure with:
   - Cold open with a fun hook or joke
   - Smooth transitions using callbacks to earlier jokes
   - A special "fun facts" segment
   - Running gags throughout
5. Make complex topics FUN and MEMORABLE
6. Include moments where hosts:
   - Finish each other's sentences
   - Have "aha!" moments
   - Use creative analogies
   - Make listeners laugh while learning

Remember: This should feel like two best friends explaining something cool they just learned, not a lecture!"""
    
    def _build_user_prompt(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        structure: Dict[str, Any],
        duration_minutes: int,
        custom_instructions: Optional[str]
    ) -> str:
        """Build the user prompt with document content."""
        # For large documents, create a summary first
        word_count = metadata.get('word_count', 0)
        
        # If document is very large, truncate intelligently
        if word_count > 3000:
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Take key sections
            first_section = '\n'.join(lines[:int(total_lines * 0.3)])
            middle_section = '\n'.join(lines[int(total_lines * 0.4):int(total_lines * 0.6)])
            last_section = '\n'.join(lines[int(total_lines * 0.8):])
            
            content = f"{first_section}\n\n[... content truncated ...]\n\n{middle_section}\n\n[... content truncated ...]\n\n{last_section}"
            
        # Calculate target word count based on duration (150 words per minute average)
        target_words = duration_minutes * 150
        
        prompt = f"""Transform this document into a FUN, ENGAGING dialogue podcast script between Alex and Sam.

Document Title: {metadata.get('title', 'Untitled')}
Word Count: {metadata.get('word_count', 0)}
Target Duration: {duration_minutes} minutes ({target_words} words of dialogue)

Document Content:
---
{content}
---

Requirements:
1. Start with a HILARIOUS cold open that hooks listeners
2. Make the introduction feel like friends discovering something cool
3. Turn boring facts into EXCITING revelations with "Did you know?!" moments
4. Include at least 3 funny analogies or comparisons
5. Add a "Fun Facts Lightning Round" segment
6. Create at least 2 running jokes that callback throughout
7. Include moments of genuine surprise and "mind-blown" reactions
8. End with a memorable sign-off and teaser for next episode
9. Make listeners LAUGH while they LEARN
10. If the topic seems dry, make it RIDICULOUSLY entertaining!

Remember: Every minute should have at least one laugh or "wow" moment!"""
        
        if custom_instructions:
            prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"
        
        return prompt
    
    def _format_dialogue_script(
        self, 
        dialogue_data: PodcastDialogue, 
        metadata: Dict[str, Any],
        tone: str,
        audience: str
    ) -> str:
        """Format the structured dialogue into a markdown script."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format dialogue sections
        def format_dialogue_section(lines: list[DialogueLine]) -> str:
            formatted = []
            for line in lines:
                tone_indicator = f" *[{line.tone}]*" if line.tone else ""
                formatted.append(f"**{line.speaker}**: {line.text}{tone_indicator}")
            return "\n\n".join(formatted)
        
        formatted_script = f"""# Podcast Script: {dialogue_data.title}

## Metadata
- Source: {metadata.get('filename', 'Unknown')}
- Duration: ~{dialogue_data.estimated_duration_minutes} minutes
- Style: Two-Host Dialogue
- Hosts: Alex & Sam
- Tone: {tone}
- Audience: {audience}
- Generated: {timestamp}
- Model: OpenAI gpt-4.1-mini (via Agents SDK)

## Script

### 🎬 COLD OPEN

{format_dialogue_section(dialogue_data.cold_open)}

### 🎙️ INTRODUCTION

{format_dialogue_section(dialogue_data.introduction)}

### 📚 MAIN CONTENT

{format_dialogue_section(dialogue_data.main_content)}

### 🎉 FUN FACTS LIGHTNING ROUND

{format_dialogue_section(dialogue_data.fun_facts_segment)}

### 👋 CONCLUSION

{format_dialogue_section(dialogue_data.conclusion)}

---
*Generated by Listen-in - Transform boring documents into fun podcasts!*
"""
        
        return formatted_script