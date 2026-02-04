# Tool Specification: mshtools-search_image_by_text

## Overview
Web image search API functioning like Google Image Search. Returns matching images with titles, descriptions, and URLs.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "queries": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Search queries (executed in parallel)"
    },
    "total_count": {
      "type": "integer",
      "default": 10,
      "minimum": 1,
      "maximum": 10,
      "description": "Maximum images to return per query"
    },
    "download_dir": {
      "type": "string",
      "description": "Directory to save images (optional)"
    },
    "need_download": {
      "type": "boolean",
      "default": false,
      "description": "Whether to download images locally"
    }
  },
  "required": ["queries"]
}
```

## Streaming Mechanism
- **Search Provider**: Integrated image search index
- **Response Format**:
  ```
  # Found N results
  # [1] (URL) Title
  [source 1](image_url)
  <thumbnail>
  ```
- **Parallel Execution**: All queries run simultaneously
- **Result Aggregation**: Shared total_count across all queries

## Integration Architecture
- **External Service**: Image search API endpoint
- **CDN**: Images served via HTTPS from various sources
- **Display**: Thumbnails rendered inline in chat

## Usage Patterns

### Basic Search
```
search_image_by_text(queries=["Marie Curie portrait"], total_count=3)
```

### Multiple Queries
```
search_image_by_text(
  queries=["cat", "dog", "bird"],
  total_count=5
)
# Returns up to 5 images total across all queries
```

### Download Images
```
search_image_by_text(
  queries=["product photo"],
  need_download=true,
  download_dir="/mnt/kimi/output/images"
)
```

## Content Rules
- **Context Matters**: Add context for better results (e.g., "Marie Curie portrait photo" not just "Marie Curie")
- **HTTPS Only**: All URLs use HTTPS protocol
- **URL Integrity**: Never modify returned URLs
