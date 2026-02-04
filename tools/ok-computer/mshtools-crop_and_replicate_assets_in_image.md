# Tool Specification: mshtools-crop_and_replicate_assets_in_image

## Overview
Asset extraction tool that crops visual elements from screenshots based on bounding boxes, with optional transparency support.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "input_url": {
      "type": "string",
      "description": "Source image URL or local path"
    },
    "bbox": {
      "type": "string",
      "description": "JSON array of bounding boxes: '[(x1,y1,x2,y2), ...]' relative coordinates 0-1"
    },
    "transparent": {
      "type": "string",
      "description": "JSON array: '[true, false, ...]' matching bbox length, true for PNG transparency"
    }
  },
  "required": ["input_url", "bbox", "transparent"]
}
```

## Streaming Mechanism
- **Processing**:
  1. Load source image
  2. For each bbox: crop region
  3. If transparent=true: background removal + PNG
  4. If transparent=false: JPEG output
  5. Save to generated paths
  6. Return list of output file paths

## Output Format
```
Generated assets: /path/to/asset1.png, /path/to/asset2.jpg
```

## Integration Architecture
- **Image Processing**: Pillow/PIL backend with alpha compositing
- **Background Removal**: ML-based segmentation for transparent outputs

## Usage Pattern

### Extract Website Assets
```
find_asset_bbox(input_url="screenshot.png")
# Returns: [{"item": "hero", "bbox": [0.0, 0.0, 1.0, 0.3]}, ...]

crop_and_replicate_assets_in_image(
  input_url="screenshot.png",
  bbox="[(0.0, 0.0, 1.0, 0.3), (0.2, 0.5, 0.4, 0.7)]",
  transparent="[true, false]"
)
# Returns: /output/hero.png, /output/icon.jpg
```

## Related Tools
- `find_asset_bbox`: Get bounding boxes first
