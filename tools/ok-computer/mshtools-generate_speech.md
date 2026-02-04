# Tool Specification: mshtools-generate_speech

## Overview
Text-to-speech conversion using ElevenLabs voices. Supports multiple output formats and voice characteristics.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Text to convert to speech"
    },
    "voice_id": {
      "type": "string",
      "description": "Voice ID from get_available_voices"
    },
    "output_path": {
      "type": "string",
      "description": "Absolute path to save audio file (.mp3, .wav)"
    }
  },
  "required": ["text", "voice_id", "output_path"]
}
```

## Streaming Mechanism
- **Synthesis Pipeline**:
  1. Text preprocessing (punctuation handling)
  2. Voice model inference
  3. Audio generation
  4. Format encoding (MP3/WAV)
  5. File write to output_path

## Output Formats
- **MP3**: Default, high quality, compressed
- **WAV**: Uncompressed, lossless

## Integration Architecture
- **Provider**: ElevenLabs API
- **Model**: Neural TTS (specific model varies by voice)
- **Streaming**: Synchronous (full generation before return)

## Usage Patterns

### Basic TTS
```
generate_speech(
  text="Hello, this is a test.",
  voice_id="21m00Tcm4TlvDq8ikWAM",
  output_path="/mnt/kimi/output/hello.mp3"
)
```

### Long Text Strategy
- Break long texts into smaller segments (<500 chars)
- Improves quality and allows retry on partial failures

## Related Tools
- `get_available_voices`: Select voice_id first
