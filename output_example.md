# Listen-in Podcast Generation Output Example

## Workflow for GDPR Document

### 1. Input Document
- **Source**: `/Users/adamanzuoni/Downloads/CELEX_32016R0679_EN_TXT.pdf`
- **Converted to**: `/Users/adamanzuoni/listen-in/examples/gdpr_excerpt_test.txt`

### 2. Generated Podcast Script
- **Output Path**: `~/Desktop/listen-in-output/gdpr_excerpt_test_podcast_20250607_160006.md`
- **Content**: Natural, conversational script with:
  - Engaging introduction
  - [PAUSE] markers for natural breathing
  - [EMPHASIS] markers for important points
  - Analogies to explain complex legal concepts
  - ~5 minutes speaking time

### 3. Generated Audio File
- **Output Path**: `~/Desktop/listen-in-output/gdpr_excerpt_test_podcast_20250607_160006.mp3`
- **Voice**: Rachel (default female podcast voice)
- **Quality**: Standard (128kbps)
- **Format**: MP3

## Example Script Preview

From the GDPR podcast script:

```
[INTRO MUSIC FADES]

Hey there, and welcome to today's episode where we're diving into something that affects every single one of us who uses the internet - the GDPR. Now, I know what you're thinking [PAUSE] "Oh great, another boring legal document." But stick with me here, because this one's actually pretty fascinating.

[EMPHASIS] The GDPR - or General Data Protection Regulation if we're being formal - is basically the European Union's way of saying "Hey, big tech companies, you can't just do whatever you want with people's personal information anymore."

Think of it this way [PAUSE] imagine if every time you walked into a store, they could follow you home, peek through your windows, go through your mail, and then sell all that information to whoever wanted it. Sounds creepy, right? Well, that's kind of what was happening online before GDPR came along in 2016.
```

## Voice Options

You can generate with different voices:
- `voice_name="rachel"` - Professional female (default)
- `voice_name="adam"` - Male voice
- `voice_name="bella"` - Friendly female
- `voice_name="matthew"` - Professional male

## Quality Options
- `quality="standard"` - 128kbps (default)
- `quality="high"` - 192kbps (+20% cost)
- `quality="ultra"` - 192kbps best (+50% cost)