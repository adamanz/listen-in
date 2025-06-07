# Listen-in Architecture

## System Overview

```mermaid
graph TB
    subgraph "Input Sources"
        TXT[Text Files<br/>.txt]
        PDF[PDF Files<br/>.pdf]
    end
    
    subgraph "MCP Server"
        SERVER[FastMCP Server<br/>listen_in.server]
    end
    
    subgraph "Parsers"
        TXTPARSER[Text Parser]
        PDFPARSER[PDF Parser]
    end
    
    subgraph "Generators"
        MONO[Monologue Generator]
        DIALOGUE[Dialogue Generator<br/>Alex & Sam]
        AGENT[Agent Generator<br/>gpt-4.1-mini]
    end
    
    subgraph "Audio Generators"
        AUDIO[Audio Generator<br/>ElevenLabs Projects]
        SIMPLEAUDIO[Simple Dialogue Audio<br/>ElevenLabs TTS]
    end
    
    subgraph "Output"
        SCRIPT[Podcast Script<br/>.md]
        MP3[Audio File<br/>.mp3]
    end
    
    TXT --> SERVER
    PDF --> SERVER
    
    SERVER --> TXTPARSER
    SERVER --> PDFPARSER
    
    TXTPARSER --> MONO
    TXTPARSER --> DIALOGUE
    TXTPARSER --> AGENT
    
    PDFPARSER --> MONO
    PDFPARSER --> DIALOGUE
    PDFPARSER --> AGENT
    
    MONO --> SCRIPT
    DIALOGUE --> SCRIPT
    AGENT --> SCRIPT
    
    SCRIPT --> AUDIO
    SCRIPT --> SIMPLEAUDIO
    
    AUDIO --> MP3
    SIMPLEAUDIO --> MP3
```

## Component Details

### Input Layer
- **Text Files**: Plain text documents (.txt)
- **PDF Files**: PDF documents with text extraction

### Parsing Layer
- **TextParser**: Extracts content, metadata, and structure from text files
- **PDFParser**: Uses pdfplumber/PyPDF2 to extract text from PDFs

### Generation Layer
- **MonologueGenerator**: Single-host podcast scripts
- **DialogueGenerator**: Two-host conversations with Alex (enthusiastic) and Sam (witty expert)
- **AgentGenerator**: Uses OpenAI Agents SDK with structured output

### Audio Layer
- **AudioGenerator**: Uses ElevenLabs Projects API for complex productions
- **SimpleDialogueAudioGenerator**: Direct TTS API for dialogue scripts

### Output Layer
- **Podcast Scripts**: Markdown files with metadata and formatted content
- **Audio Files**: MP3 files generated from scripts
</content>
</invoke>