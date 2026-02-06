> **Original analysis by the repository maintainer, licensed under CC BY 4.0.**
> Code snippets shown below are excerpted from extracted source code for
> commentary and criticism purposes.

# PDF Viewer Analysis
## `/app/pdf-viewer/` — Chrome Extension for PDF Rendering

---

## Executive Summary

The `pdf-viewer/` directory contains a Chrome extension implementing Mozilla's PDF.js library for in-browser PDF rendering. This extension loads through `browser_guard.py` to enable PDF viewing without external applications. It intercepts PDF URLs and renders them using HTML5 Canvas and JavaScript.

---

## Directory Structure

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

## Extension Identity

**Manifest Analysis**

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

**Permissions Analysis**

The extension requests several permissions. The `alarms` permission enables scheduled tasks. This is low risk. The `declarativeNetRequestWithHostAccess` permission enables URL interception. This is medium risk. The `webRequest` permission enables network monitoring. This is also medium risk. The `tabs` and `webNavigation` permissions enable tab and navigation management. These are low risk. The `storage` permission enables settings persistence. This is low risk.

The `host_permissions: <all_urls>` setting grants universal access. This is high risk. The extension can interact with any website.

---

## PDF Skill Integration

**Connection to PDF Skill**

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

**How It Works**

The PDF skill generates PDFs through two routes. The HTML route uses Playwright with Paged.js. The LaTeX route uses Tectonic. The `browser_guard.py` launches Chromium with `--load-extension=/app/pdf-viewer`. The extension intercepts PDF URLs via `declarativeNetRequestWithHostAccess`. PDF.js renders the PDF using HTML5 Canvas in `viewer.html`. The user views the PDF directly in the browser tab.

**No Direct Code Dependency**

The PDF Viewer extension and PDF skill are independent components. The PDF skill creates and processes PDFs using Python, Node.js, and LaTeX. The PDF Viewer extension views PDFs in the browser using JavaScript. They do not share code. Both use the browser but connect only through it.

---

## Technical Implementation

**PDF.js Core**

The `viewer.js` file implements PDF document parsing, page rendering through Canvas, text layer extraction, annotation handling, search functionality, and zoom and navigation controls.

**CMap Files**

The `content/web/cmaps/` directory contains character-to-glyph mapping files for CJK fonts. There are approximately 50 `.bcmap` files. Examples include `78-EUC-H.bcmap` for JIS X 0208, `GB-EUC-H.bcmap` for GB 2312, and `UniCNS-UTF8-H.bcmap` for Unicode CNS.

**Standard Fonts**

The `content/web/standard_fonts/` directory contains the 12 PDF Standard Type 1 Fonts. These include Courier in four variants, Helvetica in four variants, and Times in four variants.

**Localization**

The `content/web/locale/` directory contains translations for approximately 100 languages. These include English, German, French, Spanish, Chinese, Japanese, Korean, Arabic, Hebrew, and Hindi among others.

---

## Security Analysis

**Extension Security**

The extension code runs sandboxed in the extension context. File access is read-only since this is a viewer only. Network access follows same-origin policy for PDF loading. The universal host permission is high risk but necessary for intercepting PDFs on any site.

**Content Security Policy**

```json
"content_security_policy": {
  "extension_pages": "script-src 'self' 'wasm-unsafe-eval'; object-src 'self'"
}
```

The policy allows WebAssembly execution required for PDF.js performance. No inline scripts are permitted.

**Risk Mitigation**

Universal host access is mitigated by the extension only reading PDFs, not modifying pages. WebAssembly execution is required for performance and the code is audited. Content script injection is limited to PDF URLs.

---

## Browser Integration

**Loading in browser_guard.py**

```python
args = [
    # ... other flags
    "--load-extension=/app/pdf-viewer",
    # ...
]
```

**Runtime Behavior**

Chrome starts with the extension pre-loaded. The extension registers URL interception rules. When a PDF URL is detected, it redirects to `viewer.html`. PDF.js fetches and renders the PDF content.

---

## Inter-Module Relationships

```
pdf-viewer/
    ├── browser_guard.py (loads extension)
    │   └── Chromium (host browser)
    ├── PDF Skill (creates PDFs)
    │   └── Output PDF files
    └── User (views PDFs)
```

---

## Code Metrics

The extension contains 387 total files. The JavaScript code spans approximately 50,000 lines in PDF.js. There are roughly 50 CMap files, 12 font files, and approximately 100 locale files.

---

## Source Location

The extension source is in `source-code/pdf-viewer/` (original location: `/app/pdf-viewer/`).

---

*Document Version: 1.0*
*Analysis Date: 2026-02-02*
