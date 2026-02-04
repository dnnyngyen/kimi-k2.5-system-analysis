# Tool Specification: search_image_by_text (Base Chat)

## Overview
Web image search for Base Chat. Same functionality as OK Computer version but without mshtools- prefix.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "queries": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Search queries"
    },
    "total_count": {
      "type": "integer",
      "default": 10,
      "max": 10,
      "description": "Max images to return"
    }
  },
  "required": ["queries"]
}
```

## Streaming Mechanism
Same as OK Computer mshtools-search_image_by_text.

## Usage
```
search_image_by_text(queries=["capybara"], total_count=5)
```

## Note
Functionality identical to OK Computer version. Naming difference only reflects environment namespace.
