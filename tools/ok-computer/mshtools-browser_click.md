# Tool Specification: mshtools-browser_click

## Overview
Mouse click automation for interactive web elements. Performs clicks on buttons, links, form elements, and JavaScript-enabled components.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL of page to interact with"
    },
    "citation_id": {
      "type": "integer",
      "description": "Citation ID from browser_visit to reference existing tab"
    },
    "element_index": {
      "type": "integer",
      "description": "Zero-based index of element from browser_visit element list"
    }
  },
  "required": ["element_index"]
}
```

## Streaming Mechanism
- **Transport**: CDP Input.dispatchMouseEvent
- **Action Sequence**:
  1. Element validation (check if index exists)
  2. Scroll into view if needed
  3. Mouse move to element center
  4. Mouse down + up (click)
  5. Wait for page stabilization
  6. Return updated page state
- **Side Effects**: May trigger navigation, form submission, AJAX requests
- **Return**: Updated element list, URL, title (same format as browser_visit)

## Integration Architecture

### CDP Protocol
```javascript
// Chrome DevTools Protocol commands
Input.dispatchMouseEvent({
  type: 'mousePressed',
  x: elementCenterX,
  y: elementCenterY,
  button: 'left',
  clickCount: 1
})
Input.dispatchMouseEvent({
  type: 'mouseReleased',
  x: elementCenterX,
  y: elementCenterY,
  button: 'left',
  clickCount: 1
})
```

### Element Coordinate Resolution
- Elements identified by index from most recent browser_visit
- Coordinates calculated from bounding box client rects
- Viewport-relative positioning
- Automatic scrolling if element outside viewport

## Usage Patterns

### Basic Click
```
browser_visit(url="https://example.com")           # Get element list
browser_click(citation_id=1, element_index=3)     # Click element #3
```

### Form Submission
```
browser_input(citation_id=1, element_index=2, content="username")
browser_input(citation_id=1, element_index=3, content="password")
browser_click(citation_id=1, element_index=5)     # Submit button
```

### Navigation Chain
```
browser_visit(url="https://shop.example.com")
browser_click(element_index=2)                     # Category link
browser_click(element_index=7)                     # Product link
browser_click(element_index=4)                     # Add to cart
```

## Error Handling
- **Invalid Index**: Error if element_index >= element count
- **Stale Element**: Error if element no longer in DOM
- **Intercepted Click**: Error if overlay blocks interaction
- **Navigation Timeout**: Error if page load exceeds threshold

## Related Tools
- `browser_visit`: Required first to get element indices
- `browser_input`: Fill forms before clicking
- `browser_find`: Locate elements by text when index unknown
