# Tool Specification: search_image_by_image (Base Chat)

## Overview
Reverse image search for Base Chat. Same functionality as OK Computer version.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "image_url": {
      "type": "string",
      "description": "URL or local path to source image"
    },
    "total_count": {
      "type": "integer",
      "default": 10,
      "max": 10
    }
  },
  "required": ["image_url"]
}
```

## Usage
```
search_image_by_image(image_url="/mnt/kimi/upload/photo.jpg")
```

## Note
Identical to OK Computer mshtools-search_image_by_image.
