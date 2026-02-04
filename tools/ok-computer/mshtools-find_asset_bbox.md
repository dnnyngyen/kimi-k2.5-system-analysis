# Tool Specification: mshtools-find_asset_bbox

## Overview
Computer vision tool for identifying visual elements in webpage screenshots that require external image assets (photos, illustrations, textures).

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "input_url": {
      "type": "string",
      "description": "Image URL or local absolute file path to webpage screenshot"
    }
  },
  "required": ["input_url"]
}
```

## Streaming Mechanism
- **Analysis Pipeline**:
  1. Load screenshot image
  2. Detect visual elements that CANNOT be code-generated
  3. Filter out: 3D shapes, particles, gradients, vector UI, icons, text
  4. Identify: Photography, narrative illustrations, organic textures
  5. Return bounding boxes with descriptions

## Output Format
```json
[
  {"item": "hero background photo", "bbox": [0.380, 0.028, 0.620, 0.082]},
  {"item": "product image", "bbox": [0.0, 0.0, 1.0, 0.500]}
]
```

**bbox format**: [x1, y1, x2, y2] as relative coordinates (0-1)

## Integration Architecture
- **Vision Model**: Object detection backend
- **Classification**: Distinguishes code-generatable vs must-extract assets
- **Heuristics**: Ignores CSS-generable graphics, focuses on photographic content

## Usage Pattern

### Web Replication Workflow
```
screenshot_web_full_page(url="https://target-site.com")
find_asset_bbox(input_url="/mnt/kimi/output/screenshot.png")
# Returns list of assets needing extraction
```

## Related Tools
- `crop_and_replicate_assets_in_image`: Extract identified assets
