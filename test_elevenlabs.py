import asyncio
from fastmcp import Client
import json

async def test_elevenlabs_server():
    """Test the ElevenLabs MCP server."""
    # Create a client pointing to our server
    client = Client("elevenlabs_server.py")
    
    async with client:
        print("🔌 Connected to ElevenLabs MCP server\n")
        
        # 1. Check API status
        print("1️⃣ Checking API status...")
        try:
            status_result = await client.call_tool("check_api_status", {})
            status = json.loads(status_result[0].text)
            print(f"API Key Configured: {status.get('api_key_configured')}")
            print(f"API Reachable: {status.get('api_reachable')}")
            if "user_info" in status:
                print(f"User Tier: {status['user_info']['subscription']['tier']}")
        except Exception as e:
            print(f"Error checking status: {e}")
        print()
        
        # 2. List available voices
        print("2️⃣ Listing available voices...")
        try:
            voices_result = await client.call_tool("list_voices", {})
            voices = json.loads(voices_result[0].text)
            if voices:
                print(f"Found {len(voices)} voices:")
                for voice in voices[:5]:  # Show first 5 voices
                    print(f"  - {voice['name']} ({voice['voice_id']})")
            else:
                print("No voices found (check API key or server logs)")
        except Exception as e:
            print(f"Error listing voices: {e}")
        print()
        
        # 3. Test text-to-speech (if API key is configured)
        print("3️⃣ Testing text-to-speech...")
        try:
            tts_result = await client.call_tool("text_to_speech", {
                "text": "Hello from FastMCP! This is a test of the ElevenLabs text-to-speech integration.",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                "stability": 0.5,
                "similarity_boost": 0.5
            })
            
            result = json.loads(tts_result[0].text)
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"✅ Success! Generated {result['audio_size_bytes']} bytes of audio")
                print(f"   Format: {result['format']}")
                print(f"   Voice ID: {result['voice_id']}")
                print(f"   Model: {result['model_id']}")
                # Note: audio_base64 contains the actual audio data
        except Exception as e:
            print(f"Error generating speech: {e}")
        print()
        
        # 4. Test resource access
        print("4️⃣ Testing resource access...")
        try:
            voices_resource_result = await client.read_resource("resource://voices/list")
            voices_resource = json.loads(voices_resource_result[0].text)
            if voices_resource:
                print(f"✅ Resource returned {len(voices_resource)} items")
            else:
                print("Resource returned empty")
        except Exception as e:
            print(f"Error accessing resource: {e}")

if __name__ == "__main__":
    print("🚀 ElevenLabs MCP Server Test\n")
    asyncio.run(test_elevenlabs_server()) 