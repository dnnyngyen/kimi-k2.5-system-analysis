# Tool Specification: mshtools-get_available_voices

## Overview
Voice library browser for text-to-speech generation. Returns available voice IDs with characteristics, descriptions, and use case recommendations.

## JSON Schema
```json
{
  "type": "object",
  "properties": {}
}
```

## Streaming Mechanism
- **Source**: ElevenLabs voice library integration
- **Return Format**: List of voice metadata
  ```
  voice_id: {id}, desc: {description}
  voice_id: {id2}, desc: {description2}
  ```
- **Categories**: Professional, Casual, Character, Multilingual, Specialized

## Voice Characteristics
- **Description**: Personality and tone details
- **Language Support**: Available languages and accents  
- **Voice Type**: Gender, age, style information
- **Use Cases**: Recommended applications

## Integration Architecture
- **Provider**: ElevenLabs voice technology
- **Real-time**: Live availability checking

## Usage Pattern
```
get_available_voices()
# Review descriptions to find best match
# Note voice IDs for use in generate_speech
```

## Related Tools
- `generate_speech`: Use voice_id from this listing
