# Tool Specification: mshtools-screenshot_web_full_page

## Overview
Full-page screenshot using segmented stitching. Handles virtual scrolling pages by detecting fixed navigation, capturing viewport-sized segments, and stitching into single image.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL to capture"
    }
  }
}
```

## Streaming Mechanism
- **Algorithm**:
  1. Detect fixed/sticky headers (hide during capture)
  2. Determine full page height
  3. Scroll to top
  4. Capture viewport, scroll down, repeat
  5. Stitch segments vertically
  6. Restore fixed elements
- **Output**: Single PNG of full scrollable content

## Integration Architecture

### Multi-Shot Technique
```javascript
// Pseudocode
const height = document.body.scrollHeight;
const viewport = window.innerHeight;
const shots = [];
for (let y = 0; y < height; y += viewport) {
  window.scrollTo(0, y);
  shots.push(await captureScreenshot());
}
return stitchVertically(shots);
```

## Usage Patterns

### Document Full Page
```
screenshot_web_full_page(url="https://long-article.example.com")
# Returns stitched image of entire article
```

### Compare Before/After
```
screenshot_web_full_page(url="https://site.com/before")
# ... make changes ...
screenshot_web_full_page(url="https://site.com/after")
```

## Limitations
- **Memory**: Large pages may fail due to memory constraints
- **Fixed Elements**: May appear multiple times if not properly hidden
- **Lazy Loading**: May trigger new content during scroll sequence
