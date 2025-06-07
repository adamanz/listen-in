#!/bin/bash

echo "Testing Text-to-Speech directly..."
echo

# Test 1: Direct HTTP call to ElevenLabs server
echo "1. Testing direct HTTP call to ElevenLabs server:"
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "text_to_speech",
      "arguments": {
        "text": "This is a direct test to the ElevenLabs server."
      }
    }
  }' | jq '.'

echo
echo "2. Check if file was created:"
ls -la ~/Desktop/tts_*.mp3 | tail -5

echo
echo "3. Testing with all parameters:"
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "text_to_speech",
      "arguments": {
        "text": "Testing with all parameters specified.",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "model_id": "eleven_monolingual_v1",
        "stability": 0.5,
        "similarity_boost": 0.5
      }
    }
  }' | jq '.result | {text_length, file_path, success}' 