# PDF Viewer Analysis
## `/app/pdf-viewer/` — Chrome Extension for PDF Rendering

---

## Executive Summary

The `pdf-viewer/` directory contains a Chrome extension implementing Mozilla's PDF.js library for in-browser PDF rendering. This extension is loaded by `browser_guard.py` to enable PDF viewing without external applications. The extension intercepts PDF URLs and renders them using HTML5 Canvas and JavaScript.

---

## 1. Directory Structure

```
pdf-viewer/
├── manifest.json              # Extension manifest (v3)
├── preferences_schema.json    # Settings schema
├── background.js              # Service worker
├── contentscript.js           # Content script injection
├── contentstyle.css           # Content script styles
├── extension-router.js        # URL routing logic
├── pdfHandler.js              # PDF handling logic
├── preserve-referer.js        # Referer preservation
├── suppress-update.js         # Update suppression
├── telemetry.js               # Usage analytics
├── icon16.png                 # Extension icons
├── icon48.png
├── icon128.png
├── options/                   # Options page
│   └── options.html
└── content/
    └── web/
        ├── cmaps/             # CJK character maps (~50 files)
        ├── images/            # UI icons
        ├── locale/            # Translations (~100 files)
        ├── standard_fonts/    # PDF standard Type 1 fonts (12 files)
        ├── viewer.html        # Main viewer HTML
        └── viewer.js          # PDF.js viewer implementation
```

---

## 2. Extension Identity

### 2.1 Manifest Analysis

```json
{
  "minimum_chrome_version": "103",
  "manifest_version": 3,
  "name": "PDF Viewer",
  "version": "4.6.129",
  "description": "Uses HTML5 to display PDF files directly in the browser.",
  "permissions": [
    "alarms",
    "declarativeNetRequestWithHostAccess",
    "webRequest",
    "tabs",
    "webNavigation",
    "storage"
  ],
  "host_permissions": ["<all_urls>"],
  "content_scripts": [{
    "matches": ["http://*/*", "https://*/*", "file://*/*"],
    "run_at": "document_start",
    "all_frames": true,
    "css": ["contentstyle.css"],
    "js": ["contentscript.js"]
  }],
  "background": {
    "service_worker": "background.js"
  },
  "web_accessible_resources": [{
    "resources": ["content/web/viewer.html", "http:/*", "https:/*", ...],
    "matches": ["<all_urls>"],
    "extension_ids": ["*"]
  }]
}
```

### 2.2 Permissions Analysis

| Permission | Purpose | Risk |
|------------|---------|------|
| `alarms` | Scheduled tasks | Low |
| `declarativeNetRequestWithHostAccess` | URL interception | Medium |
| `webRequest` | Network monitoring | Medium |
| `tabs` | Tab management | Low |
| `webNavigation` | Navigation events | Low |
| `storage` | Settings persistence | Low |
| `host_permissions: <all_urls>` | Universal access | **HIGH** |

---

## 3. PDF Skill Integration

### 3.1 Connection to PDF Skill

```
PDF Skill (Creation/Processing)
    │
    ├── HTML Route ──► Playwright ──► Chromium
    │                                   │
    │                                   ├── PDF Viewer Extension
    │                                   │   └── Renders PDFs in browser
    │                                   │
    └── LaTeX Route ──► Tectonic ──► PDF output
```

### 3.2 How It Works

1. **PDF Creation**: PDF skill generates PDF via HTML+Paged.js or LaTeX+Tectonic
2. **Browser Loading**: `browser_guard.py` launches Chromium with `--load-extension=/app/pdf-viewer`
3. **URL Interception**: Extension intercepts PDF URLs via `declarativeNetRequestWithHostAccess`
4. **Rendering**: PDF.js renders PDF using HTML5 Canvas in `viewer.html`
5. **Display**: User views PDF directly in browser tab

### 3.3 No Direct Code Dependency

**Important**: The PDF Viewer extension and PDF skill are **independent components**:

| Aspect | PDF Skill | PDF Viewer |
|--------|-----------|------------|
| **Purpose** | Create/process PDFs | View PDFs in browser |
| **Technology** | Python/Node.js/LaTeX | JavaScript (PDF.js) |
| **Output** | PDF files | Rendered view |
| **Integration** | Via browser automation | Via Chrome extension |

**Connection Point**: Both use the browser, but don't share code directly.

---

## 4. Technical Implementation

### 4.1 PDF.js Core

**viewer.js** implements:
- PDF document parsing
- Page rendering (Canvas-based)
- Text layer extraction
- Annotation handling
- Search functionality
- Zoom/navigation controls

### 4.2 CMap Files (`content/web/cmaps/`)

**Purpose**: Character-to-glyph mapping for CJK fonts.

**Count**: ~50 `.bcmap` files

**Examples**:
- `78-EUC-H.bcmap` — JIS X 0208 (1978), EUC encoding, horizontal
- `GB-EUC-H.bcmap` — GB 2312, EUC encoding, horizontal
- `UniCNS-UTF8-H.bcmap` — Unicode CNS (Taiwan), UTF-8, horizontal

### 4.3 Standard Fonts (`content/web/standard_fonts/`)

**PDF Standard Type 1 Fonts**:
- Courier (4 variants)
- Helvetica (4 variants)
- Times (4 variants)

**Total**: 12 OTF files

### 4.4 Localization (`content/web/locale/`)

**Supported Languages**: ~100

**Examples**: en, de, fr, es, zh-CN, zh-TW, ja, ko, ar, he, hi

---

## 5. Security Analysis

### 5.1 Extension Security

| Aspect | Assessment |
|--------|------------|
| **Code execution** | Sandboxed in extension context |
| **File access** | Read-only (viewer only) |
| **Network access** | Same-origin for PDF loading |
| **Host permissions** | `<all_urls>` — **HIGH RISK** |

### 5.2 Content Security Policy

```json
"content_security_policy": {
  "extension_pages": "script-src 'self' 'wasm-unsafe-eval'; object-src 'self'"
}
```

- `wasm-unsafe-eval`: Required for PDF.js WebAssembly optimizations
- No inline scripts allowed

### 5.3 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Universal host access | Extension only reads PDFs, doesn't modify |
| WebAssembly execution | Required for performance, code is audited |
| Content script injection | Limited to PDF URLs |

---

## 6. Browser Integration

### 6.1 Loading in browser_guard.py

```python
args = [
    # ... other flags
    "--load-extension=/app/pdf-viewer",
    # ...
]
```

### 6.2 Runtime Behavior

1. Chrome starts with extension pre-loaded
2. Extension registers URL interception rules
3. When PDF URL detected, redirects to `viewer.html`
4. PDF.js fetches and renders PDF content

---

## 7. Inter-Module Relationships

```
pdf-viewer/
    ├── browser_guard.py (loads extension)
    │   └── Chromium (host browser)
    ├── PDF Skill (creates PDFs)
    │   └── Output PDF files
    └── User (views PDFs)
```

---

## 8. Code Metrics

| Metric | Value |
|--------|-------|
| Total Files | 387 |
| JavaScript | ~50,000 lines (PDF.js) |
| CMap Files | ~50 |
| Font Files | 12 |
| Locale Files | ~100 |

---

*Document Version: 1.0*
*Analysis Date: 2026-02-02*
