# Tool Specification: web_open_url (Base Chat)

## Overview
Direct URL content fetcher for reading, summarizing, or analyzing specific web pages. Loads and renders content from provided URLs.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "urls": {
      "type": "array",
      "items": {"type": "string"},
      "description": "URLs to fetch and display content from"
    }
  },
  "required": ["urls"]
}
```

## Streaming Mechanism
- **Transport**: HTTP GET with browser rendering
- **Processing**: 
  1. Fetch URL content
  2. Render JavaScript (if SPA)
  3. Extract main content
  4. Convert to readable format
  5. Return with citation
- **Return**: Page content, title, metadata

## Use Cases
- User provides specific URL to analyze
- Fact-checking specific sources
- Reading documentation pages
- Summarizing articles

## Differences from browser_visit
| Aspect | web_open_url | browser_visit |
|--------|--------------|---------------|
| Environment | Base Chat | OK Computer |
| Interaction | Read-only | Full automation |
| Element List | No | Yes |
| Click/Input | No | Yes |

## Usage
```
web_open_url(urls=["https://example.com/article"])
```

## System Integration
- **Base Chat Only**: Not available in OK Computer (use browser_visit instead)
- **Citation**: Creates citation reference for content
