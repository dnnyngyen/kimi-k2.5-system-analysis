# Tool Specification: mshtools-browser_input

## Overview
Text entry automation for form fields including text inputs, textareas, and other data entry elements.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL of page with form"
    },
    "citation_id": {
      "type": "integer",
      "description": "Citation ID for existing tab"
    },
    "element_index": {
      "type": "integer",
      "description": "Zero-based index of input element"
    },
    "content": {
      "type": "string",
      "description": "Text to enter into the field"
    }
  },
  "required": ["element_index", "content"]
}
```

## Streaming Mechanism
- **Input Sequence**:
  1. Focus element (click)
  2. Clear existing content (Ctrl+A, Delete)
  3. Type content character by character
  4. Blur element (unfocus)
  5. Wait for validation/JS events
  6. Return updated page state
- **Typing Simulation**: Realistic delays between keystrokes to trigger JS events
- **Special Keys**: Supports \n for Enter, \t for Tab

## Integration Architecture

### CDP Input Domain
```javascript
// Focus
DOM.focus({ nodeId: elementId })

// Clear
Input.dispatchKeyEvent({ type: 'keyDown', key: 'Control' })
Input.dispatchKeyEvent({ type: 'keyDown', key: 'a' })
Input.dispatchKeyEvent({ type: 'keyUp', key: 'a' })
Input.dispatchKeyEvent({ type: 'keyUp', key: 'Control' })

// Type
for (const char of content) {
  Input.insertText({ text: char })
  await delay(10)  // Simulate human typing
}
```

## Supported Input Types
- `<input type="text">`
- `<input type="password">`
- `<input type="email">`
- `<input type="search">`
- `<textarea>`
- `<input type="number">` (formats as string)
- Content-editable divs

## Usage Patterns

### Login Form
```
browser_visit(url="https://login.example.com")
browser_input(citation_id=1, element_index=0, content="username")
browser_input(citation_id=1, element_index=1, content="password")
browser_click(citation_id=1, element_index=2)  # Login button
```

### Search Query
```
browser_visit(url="https://search.example.com")
browser_input(citation_id=1, element_index=0, content="query term")
browser_click(citation_id=1, element_index=1)  # Search button
```

### Multi-Field Form
```
browser_input(citation_id=1, element_index=0, content="John")
browser_input(citation_id=1, element_index=1, content="Doe")
browser_input(citation_id=1, element_index=2, content="john@example.com")
```

## Error Handling
- **Non-Input Element**: Error if element not input/textarea
- **Read-Only**: Error if field disabled or read-only
- **Validation Failure**: May return page with error messages visible

## Related Tools
- `browser_click`: Submit form or move between fields
- `browser_find`: Locate input fields by label text
