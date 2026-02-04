# Tool Specification: mshtools-generate_image

## Overview
AI image generation from text descriptions using diffusion model. Supports multiple aspect ratios, resolutions, and transparency.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "Detailed text prompt describing desired image"
    },
    "output_path": {
      "type": "string",
      "description": "Absolute path to save generated image"
    },
    "ratio": {
      "type": "string",
      "enum": ["1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9"],
      "default": "1:1",
      "description": "Aspect ratio"
    },
    "resolution": {
      "type": "string",
      "enum": ["1K", "2K", "4K"],
      "default": "1K",
      "description": "Image resolution (1K default, transparent only supports 1K)"
    },
    "background": {
      "type": "string",
      "enum": ["opaque", "transparent"],
      "default": "opaque",
      "description": "Background type (transparent only for 1:1, 3:2, 2:3 at 1K)"
    }
  },
  "required": ["description", "output_path"]
}
```

## Streaming Mechanism
- **Generation Pipeline**:
  1. Prompt processing and enhancement
  2. Diffusion model inference
  3. Post-processing (upscaling if 2K/4K)
  4. Format conversion (PNG for transparent, JPG for opaque)
  5. File write to output_path
- **Return**: Confirmation with file path

## Integration Architecture

### Model Backend
- **Provider**: External image generation service (Kimi models can't generate images) Most likely Nano🍌
- **Model**: Diffusion-based (specific architecture not exposed)
- **Compute**: GPU-accelerated inference
- **Queue**: Synchronous execution (waits for completion)

## Usage Patterns

### Basic Generation
```
generate_image(
  description="A serene mountain landscape at sunset",
  output_path="/mnt/kimi/output/mountain.jpg"
)
```

### Specific Ratio
```
generate_image(
  description="Product showcase on white background",
  output_path="/mnt/kimi/output/product.jpg",
  ratio="16:9",
  resolution="2K"
)
```

### Transparent Background
```
generate_image(
  description="Cute cartoon character",
  output_path="/mnt/kimi/output/character.png",
  ratio="1:1",
  background="transparent"
)
```

## Prompt Guidelines
- **Detail Level**: More descriptive = better results
- **Style References**: Include artistic style when desired
- **Composition**: Describe framing and perspective
- **Atmosphere**: Mention lighting and mood
- **Language**: Use same language as conversation
