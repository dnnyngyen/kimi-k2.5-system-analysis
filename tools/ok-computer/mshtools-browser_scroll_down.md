# Tool Specification: mshtools-browser_scroll_down

## Overview
Vertical scroll automation to reveal content below current viewport. Enables access to infinite scroll content, long articles, and lazy-loaded elements.

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
      "description": "Pixels to scroll down (typical: 300-1000)"
    }
  },
  "required": ["scroll_amount"]
}
```

## Streaming Mechanism
- **Scroll Execution**:
  1. Evaluate current scroll position
  2. Execute scrollBy(0, scroll_amount)
  3. Wait for stabilization (animations settle)
  4. Trigger lazy loading checks
  5. Re-scan for new interactive elements
  6. Return updated element list
- **Lazy Loading**: Triggers intersection observer callbacks
- **Element Indices**: May change due to new elements entering DOM

## Integration Architecture

### JavaScript Execution
```javascript
window.scrollBy({
  top: scroll_amount,
  behavior: 'smooth'  // or 'auto' for instant
});
```

### Stabilization Logic
- Waits for requestAnimationFrame completion
- Polls for DOM mutations settling
- Re-queries interactive elements after scroll

## Usage Patterns

### Infinite Scroll
```
browser_visit(url="https://social.example.com")
browser_scroll_down(citation_id=1, scroll_amount=800)  # Load more content
browser_scroll_down(citation_id=1, scroll_amount=800)  # Load more content
```

### Long Article
```
browser_visit(url="https://blog.example.com/article")
browser_scroll_down(citation_id=1, scroll_amount=1000)  # Read next section
```

### Element Discovery
```
browser_visit(url="https://shop.example.com")
browser_scroll_down(citation_id=1, scroll_amount=500)  # Reveal more products
```

## Related Tools
- `browser_scroll_up`: Reverse direction
- `browser_click`: Interact with newly revealed elements
- `browser_find`: Search in newly loaded content
