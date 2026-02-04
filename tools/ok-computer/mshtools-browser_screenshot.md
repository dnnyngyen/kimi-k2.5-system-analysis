# Tool Specification: mshtools-browser_screenshot

## Overview
Page capture tool for visual inspection and documentation. Returns screenshot as embedded image or saves to filesystem.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL to capture (optional, uses current page if omitted)"
    },
    "citation_id": {
      "type": "integer",
      "description": "Citation ID of tab to capture (optional)"
    },
    "download_screenshot_path": {
      "type": "string",
      "description": "Absolute path to save screenshot (optional, empty string = don't save)"
    }
  }
}
```

## Streaming Mechanism
- **Capture Method**: CDP Page.captureScreenshot
- **Format**: PNG (default)
- **Viewport**: Current browser viewport only (not full page)
- **Return**: Image data embedded in response or saved to path

## Integration Architecture

### CDP Page Domain
```javascript
Page.captureScreenshot({
  format: 'png',
  fromSurface: true
})
```

## Usage Patterns

### Capture Current Page
```
browser_visit(url="https://example.com")
browser_screenshot()  # Returns inline image
```

### Save to File
```
browser_screenshot(
  citation_id=1,
  download_screenshot_path="/mnt/kimi/output/screenshot.png"
)
```

### Visual Verification
```
browser_click(citation_id=1, element_index=3)
browser_screenshot(citation_id=1)  # Verify result
```

## Limitations
- **Viewport Only**: Captures visible area, not full scrollable page
- **Dynamic Content**: May catch loading states

## Related Tools
- `screenshot_web_full_page`: Capture full scrollable page
