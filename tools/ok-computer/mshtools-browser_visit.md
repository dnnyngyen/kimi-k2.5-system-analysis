# Tool Specification: mshtools-browser_visit

## Overview
Web page loader and renderer using Playwright-controlled Chromium 120.x browser. Provides foundation for all browser automation tasks, extracting interactive elements and creating citation references.

## JSON Schema
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "URL to load (direct or citation-based)"
    },
    "citation_id": {
      "type": "integer",
      "description": "Citation ID from previous browser_state to switch to existing tab"
    },
    "need_screenshot": {
      "type": "boolean",
      "default": false,
      "description": "Include screenshot in response"
    }
  }
}
```

## Streaming Mechanism
- **Transport**: CDP (Chrome DevTools Protocol) over HTTP/WebSocket
- **Browser Instance**: Chromium 120.x running in stealth mode
- **Page Lifecycle**:
  1. Navigation: HTTP GET with custom user-agent
  2. Rendering: Full JavaScript execution (SPA support)
  3. Stabilization: Wait for DOM ready + network idle
  4. Element Extraction: Query all interactive elements
  5. Citation Registration: Assign unique ID for session reference
- **Output**: Element list (indices, types, text), page metadata, screenshot (optional)

## Integration Architecture

### Browser Stack
```
browser_guard.py (41KB Playwright framework)
    ↓
Chromium 120.x (stealth mode)
    ↓
CDP Ports: 9222 (localhost), 9223 (public HTTP)
    ↓
Chrome Extensions: pdf-viewer (387 files for PDF rendering)
```

### Stealth Configuration
- **User-Agent**: Custom construction matching real browsers
- **Fingerprint Evasion**: Anti-detection flags enabled
- **Viewport**: Standardized to avoid detection
- **WebGL/Canvas**: Noise injection for fingerprint randomization

### Element Detection
Captures all interactive elements:
- Links (`<a>` tags)
- Buttons (`<button>`, `[role="button"]`)
- Form inputs (`<input>`, `<textarea>`, `<select>`)
- Interactive ARIA roles

Each element assigned zero-based index for subsequent interaction tools.

## Citation System
- **Session Persistence**: Tabs tracked via citation_id across tool calls
- **Cross-Reference**: Other tools use citation_id to refer to specific tabs
- **State Query**: `browser_state` returns all open tabs with citation IDs

## Usage Patterns

### Initial Navigation
```
browser_visit(url="https://example.com")
# Returns: element list, current URL, page title
```

### Tab Switching
```
browser_state()                    # List all tabs
browser_visit(citation_id=3)       # Switch to tab with ID 3
```

### With Screenshot
```
browser_visit(url="https://example.com", need_screenshot=true)
# Returns page content + visual snapshot for verification
```

## Limitations
- **Network Isolation**: Same container-level restrictions as shell (external blocked)
- **Element Indices**: Zero-based, change after scroll operations
- **Dynamic Content**: May miss elements requiring user interaction to reveal
- **Authentication**: Cannot handle complex auth flows (OAuth, CAPTCHA)

## Related Tools
- `browser_click`: Interact with elements by index
- `browser_input`: Fill form fields
- `browser_scroll_*`: Reveal more elements
- `browser_find`: Search for specific text
