# Tool Specification: mshtools-search_image_by_image

## Overview
Reverse image search (Google Lens-style). Finds visually similar images and traces original sources from an input image.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "image_url": {
      "type": "string",
      "description": "URL of image to search, OR local absolute file path"
    },
    "total_count": {
      "type": "integer",
      "default": 10,
      "maximum": 10,
      "description": "Maximum results to return"
    },
    "download_dir": {
      "type": "string",
      "description": "Directory to save similar images"
    },
    "need_download": {
      "type": "boolean",
      "default": false
    }
  },
  "required": ["image_url"]
}
```

## Streaming Mechanism
- **Input Processing**: Load image from URL or local path
- **Feature Extraction**: Compute image embedding/fingerprint
- **Similarity Search**: Query index for visually similar images
- **Result Format**: Same as search_image_by_text (title, URL, thumbnail)

## Integration Architecture
- **Vision Model**: Image understanding backend
- **Vector Index**: Similarity search infrastructure

## Usage Patterns

### Find Similar Images
```
search_image_by_image(
  image_url="https://example.com/photo.jpg",
  total_count=5
)
```

### Trace Source
```
search_image_by_image(
  image_url="/mnt/kimi/upload/mystery-image.png",
  total_count=10
)
```

## Use Cases
- Finding higher resolution versions
- Locating original source/attribution
- Finding similar products/items
- Detecting image reuse/manipulation
