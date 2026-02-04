# Tool Specification: mshtools-browser_scroll_up

## Overview
Vertical scroll automation to access content above current viewport. Enables navigation back to headers, menus, and previously viewed content.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL to scroll on"
    },
    "citation_id": {
      "type": "integer",
      "description": "Citation ID for existing tab"
    },
    "scroll_amount": {
      "type": "integer",
      "description": "Pixels to scroll up (typical: 300-1000)"
    }
  },
  "required": ["scroll_amount"]
}
```

## Streaming Mechanism
- **Scroll Execution**:
  1. Evaluate current scroll position
  2. Execute scrollBy(0, -scroll_amount)
  3. Wait for stabilization
  4. Return updated element list
- **Boundary Handling**: Stops at scrollTop=0 (page top)
- **Element Indices**: May change as elements re-enter viewport

## Usage Patterns

### Return to Header
```
browser_scroll_down(citation_id=1, scroll_amount=2000)
browser_scroll_up(citation_id=1, scroll_amount=2000)  # Back to top
```

### Navigation Menu Access
```
browser_scroll_up(citation_id=1, scroll_amount=500)  # Reveal sticky header
```

## Related Tools
- `browser_scroll_down`: Opposite direction
- `browser_visit`: Return to top instantly via refresh
