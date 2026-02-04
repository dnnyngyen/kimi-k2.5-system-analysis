# Tool Specification: web_search (Base Chat)

## Overview
General-purpose web search for Base Chat environment. Identical functionality to OK Computer's mshtools-web_search but with different namespace.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "queries": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Search queries (max 5, executed in parallel)",
      "maxItems": 5
    }
  },
  "required": ["queries"]
}
```

## Streaming Mechanism
- **Transport**: Synchronous HTTP API
- **Response**: Top results with snippets
- **Citation Format**: [^N^] format
- **Parallel**: Multiple queries per call

## Differences from OK Computer
| Aspect | Base Chat | OK Computer |
|--------|-----------|-------------|
| Prefix | None | mshtools- |
| Step Budget | 10 per turn | 200-300 per session |
| Skill Loading | No | Yes |
| Filesystem | Limited | Full /mnt/okcomputer |

## Usage
Same as mshtools-web_search but without prefix:
```
web_search(queries=["current events", "weather today"])
```

## System Integration
- **Environment**: kimi.com/chat
- **No Skills**: Cannot access /app/.kimi/skills/
- **No Persistent Filesystem**: /mnt/kimi/upload only, no output directory
- **Citation Storage**: /mnt/kimi/.store/citation.jsonl (288KB persistent)
