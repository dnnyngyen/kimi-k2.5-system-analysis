# Tool Specification: mshtools-generate_sound_effects

## Overview
AI-powered sound effect generation from text descriptions. Creates custom audio for games, video production, and UI design.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "English description of desired sound (REQUIRED: must be English)"
    },
    "duration": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 22,
      "description": "Duration in seconds"
    },
    "output_path": {
      "type": "string",
      "description": "Absolute path to save audio file"
    }
  },
  "required": ["description", "duration", "output_path"]
}
```

## Streaming Mechanism
- **Generation**: AI model interprets description and synthesizes audio
- **Duration Constraints**: 0.5-22 seconds
- **Output**: Audio file at specified path

## Sound Categories
- **Ambient**: Nature, city, indoor environments
- **Action**: Impacts, explosions, movements
- **Musical**: Melodies, rhythms, atmospheric
- **Foley**: Footsteps, doors, mechanical
- **Emotional**: Tension, relaxation, excitement
- **Abstract**: Sci-fi, fantasy, otherworldly

## Integration Architecture
- **Provider**: ElevenLabs sound generation
- **Language**: English descriptions only (mandatory)
- **Model**: Diffusion or flow-based audio generation

## Usage Patterns

### UI Sound
```
generate_sound_effects(
  description="Soft click sound, pleasant, subtle",
  duration=0.5,
  output_path="/mnt/kimi/output/click.mp3"
)
```

### Environmental Audio
```
generate_sound_effects(
  description="Gentle rain falling on leaves with distant thunder",
  duration=10,
  output_path="/mnt/kimi/output/rain.mp3"
)
```

## Duration Guidelines
- **0.5-3s**: UI sounds, notifications
- **3-10s**: Ambient loops, musical phrases
- **10-22s**: Background music, extended ambient

## Constraints
- **English Only**: Non-English descriptions rejected or produce poor results
- **Text Length**: Detailed descriptions produce better results
