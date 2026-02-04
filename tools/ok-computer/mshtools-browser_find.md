# Tool Specification: mshtools-browser_find

## Overview
Text-based element locator with automatic highlighting and scrolling. Searches for specific keywords or text across all page elements.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL to search on"
    },
    "citation_id": {
      "type": "integer",
      "description": "Citation ID for existing tab"
    },
    "keyword": {
      "type": "string",
      "description": "Text to search for (case-insensitive)"
    },
    "skip": {
      "type": "integer",
      "default": 0,
      "description": "Skip N occurrences to find subsequent matches"
    }
  },
  "required": ["keyword"]
}
```

## Streaming Mechanism
- **Search Algorithm**: Case-insensitive substring match across all text nodes
- **Result Processing**:
  1. Query all elements for text content
  2. Filter by keyword match
  3. If skip > 0: discard first N matches
  4. Scroll to first remaining match
  5. Highlight matching element
  6. Return updated page state
- **Scope**: Searches visible and hidden text content

## Integration Architecture

### JavaScript Execution
```javascript
// Injected into page context
const elements = document.querySelectorAll('*');
const matches = Array.from(elements).filter(el => 
  el.textContent.toLowerCase().includes(keyword.toLowerCase())
);
if (matches.length > skip) {
  matches[skip].scrollIntoView();
  matches[skip].style.outline = '2px solid red';  // Highlight
}
```

## Usage Patterns

### Find First Occurrence
```
browser_visit(url="https://example.com")
browser_find(citation_id=1, keyword="Submit")
```

### Find Nth Occurrence
```
browser_find(citation_id=1, keyword="Add to cart", skip=2)  # 3rd occurrence
```

### Form Label Location
```
browser_find(citation_id=1, keyword="Email Address")
# Returns page with email input field highlighted
```

## Limitations
- **Partial Matches**: "Submit" matches "Submission" 
- **Dynamic Content**: May miss elements added after page load
- **Hidden Content**: Searches hidden text but may not scroll to invisible elements

## Related Tools
- `browser_click`: Click found elements
- `browser_input`: Fill found form fields
