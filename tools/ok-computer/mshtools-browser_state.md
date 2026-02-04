# Tool Specification: mshtools-browser_state

## Overview
Session inspector displaying all open browser tabs, their URLs, and citation IDs. Enables multi-tab management and navigation debugging.

## JSON Schema
```json
{
  "type": "object",
  "properties": {}
}
```

## Streaming Mechanism
- **Query Method**: No parameters required
- **Return Format**:
  ```json
  {
    "tabs": [
      {"citation_id": 1, "url": "https://example.com", "title": "Example"},
      {"citation_id": 2, "url": "https://other.com", "title": "Other Page"}
    ]
  }
  ```
- **State Snapshot**: Current state of browser session

## Integration Architecture

### CDP Browser Domain
```javascript
Browser.getTargets()  // List all pages
```

## Usage Patterns

### Check Open Tabs
```
browser_state()
# Returns list of all tabs with citation IDs
```

### Switch to Tab
```
browser_state()                    # Find citation_id
browser_visit(citation_id=2)       # Switch to tab 2
```

### Session Cleanup
```
browser_state()  # Review before closing conversation
```

## Related Tools
- `browser_visit`: Use citation_id to switch tabs
