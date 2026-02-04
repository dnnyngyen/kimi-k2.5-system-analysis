# Supporting Directories Analysis
## `/app/data/`, `/app/pdf-viewer/`, `/app/logs/`, `/app/__pycache__/`

---

## 1. `/app/data/`: Runtime Data Storage

### 1.1 Directory Structure

```
data/
└── chrome_data/
    ├── Default/
    │   ├── Cache/                    # HTTP cache
    │   ├── Code Cache/               # V8 bytecode cache
    │   ├── Cookies                   # SQLite cookies database
    │   ├── Cookies-journal           # SQLite journal
    │   ├── DawnWebGPUCache/          # WebGPU shader cache
    │   ├── Extension Scripts/        # Extension JavaScript
    │   ├── Extension State/          # Extension storage
    │   ├── Favicons                  # Favicon database
    │   ├── GPUCache/                 # GPU shader cache
    │   ├── History                   # Browsing history
    │   ├── History-journal           # History journal
    │   ├── Local Storage/            # DOM localStorage
    │   ├── Login Data                # Saved passwords
    │   ├── Network Action Predictor  # Prefetch data
    │   ├── Preferences               # Chrome preferences JSON
    │   ├── Safe Browsing Cookies     # Security cookies
    │   ├── Secure Preferences        # Encrypted preferences
    │   ├── Session Storage/          # DOM sessionStorage
    │   ├── SharedDictionary/         # Compression dictionaries
    │   ├── Shortcuts                 # URL shortcuts
    │   ├── Site Characteristics Database/  # Site behavior
    │   ├── Top Sites                 # New tab page tiles
    │   ├── Trust Tokens              # Privacy tokens
    │   ├── Web Data                  # Autofill data
    │   ├── WebStorage/               # Storage quotas
    │   └── shared_proto_db/          # Protocol buffer DB
    ├── first_party_sets.db           # First-party sets
    ├── GraphiteDawnCache/            # Graphite cache
    ├── Local State                   # Chrome state JSON
    └── Variations                    # Field trial data
```

### 1.2 Functional Purpose

**Chrome Profile Persistence**: The `chrome_data/` directory serves as the persistent user data directory for Chromium instances launched by `browser_guard.py`.

**Key Configuration in browser_guard.py**:
```python
launch_options = {
    "user_data_dir": "/app/data/chrome_data",
    # ... other options
}
```

### 1.3 Data Categories

| Category | Files/Directories | Purpose |
|----------|-------------------|---------|
| **Authentication** | `Cookies`, `Login Data` | Session persistence, saved passwords |
| **Browsing History** | `History`, `Favicons` | URL history, favicon cache |
| **Storage** | `Local Storage/`, `Session Storage/`, `WebStorage/` | Web API storage |
| **Performance** | `Cache/`, `Code Cache/`, `GPUCache/` | Caching for performance |
| **Preferences** | `Preferences`, `Secure Preferences`, `Local State` | User settings |
| **Security** | `Safe Browsing Cookies`, `Trust Tokens` | Security features |
| **Extensions** | `Extension Scripts/`, `Extension State/` | PDF viewer extension |

### 1.4 Operational Implications

**Persistence Across Sessions**:
- Cookies survive browser restarts
- Login sessions maintained
- Extension state preserved (PDF viewer settings)
- Cache improves subsequent load times

**Security Considerations**:
- Contains sensitive data (cookies, passwords)
- Should be isolated per user/session in multi-tenant scenarios
- `Secure Preferences` encrypted but `Preferences` is plaintext JSON

---

## 2. `/app/pdf-viewer/`: Chrome PDF Extension

### 2.1 Directory Structure

```
pdf-viewer/
├── background.js              # Service worker
├── contentstyle.css           # Content script styles
├── contentscript.js           # Content script injection
├── extension-router.js        # URL routing logic
├── icon128.png                # Extension icons
├── icon16.png
├── icon48.png
├── LICENSE
├── manifest.json              # Extension manifest
├── options/                   # Options page
├── pdfHandler.js              # PDF handling logic
├── preferences_schema.json    # Settings schema
├── preserve-referer.js        # Referer preservation
├── suppress-update.js         # Update suppression
├── telemetry.js               # Usage analytics
└── content/
    └── web/
        ├── cmaps/             # Character maps (~50 files)
        │   ├── 78-EUC-H.bcmap
        │   ├── 78-EUC-V.bcmap
        │   ├── 78-H.bcmap
        │   ├── 78-RKSJ-H.bcmap
        │   └── ...
        ├── images/            # UI icons
        │   ├── annotation-*.svg
        │   ├── findbar-*.svg
        │   ├── toolbar-*.svg
        │   └── ...
        ├── locale/            # Translations (~100 files)
        │   ├── ach/
        │   ├── af/
        │   ├── am/
        │   └── ...
        ├── standard_fonts/    # PDF standard fonts
        │   ├── courier-bold.otf
        │   ├── courier-boldoblique.otf
        │   ├── courier-oblique.otf
        │   ├── courier.otf
        │   ├── helvetica-bold.otf
        │   ├── helvetica-boldoblique.otf
        │   ├── helvetica-oblique.otf
        │   ├── helvetica.otf
        │   ├── times-bold.otf
        │   ├── times-bolditalic.otf
        │   ├── times-italic.otf
        │   └── times-roman.otf
        ├── viewer.html        # Main viewer HTML
        └── viewer.js          # PDF.js viewer implementation
```

### 2.2 Extension Identity

**Manifest** (`manifest.json`):
```json
{
  "name": "PDF Viewer",
  "version": "3.0.0",
  "manifest_version": 3,
  "permissions": [
    "storage",
    "scripting"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["contentscript.js"],
      "css": ["contentstyle.css"],
      "run_at": "document_start"
    }
  ],
  "web_accessible_resources": [
    {
      "resources": ["content/web/*"],
      "matches": ["<all_urls>"]
    }
  ]
}
```

### 2.3 Technical Implementation

**PDF.js-based**: Mozilla's PDF.js library embedded as Chrome extension.

**Key Components**:

| File | Purpose |
|------|---------|
| `viewer.html` / `viewer.js` | Main PDF rendering UI |
| `cmaps/` | CMap files for CJK (Chinese, Japanese, Korean) font encoding |
| `standard_fonts/` | 14 PDF standard Type 1 fonts |
| `locale/` | i18n translations for UI strings |

### 2.4 Browser Integration

**Loading in browser_guard.py**:
```python
args = [
    # ... other flags
    "--load-extension=/app/pdf-viewer",
    # ...
]
```

**Purpose**: Enables in-browser PDF viewing without external applications.

### 2.5 CMap Files Analysis

**Purpose**: Character-to-glyph mapping for CJK fonts in PDFs.

**File Count**: ~50 `.bcmap` files

**Naming Convention**: `{encoding}-{orientation}.bcmap`
- Encoding: 78, 83, 90ms, 90msp, 90pv, Add, Adobe, B5, CNS, EUC, Ext, GB, HK, KSC, Uni
- Orientation: H (horizontal), V (vertical)

**Examples**:
- `78-EUC-H.bcmap`: JIS X 0208 (1978) EUC encoding, horizontal
- `GB-EUC-H.bcmap`: GB 2312 EUC encoding, horizontal
- `UniCNS-UTF8-H.bcmap`: Unicode CNS (Taiwan) UTF-8, horizontal

---

## 3. `/app/logs/`: Log Storage

### 3.1 Purpose

Runtime log storage for debugging and monitoring.

### 3.2 Expected Contents

Based on `browser_guard.py` configuration:
```python
"--log-file=/app/logs/chromium.log",
```

**Chromium Logs**: Browser console and debug output.

### 3.3 Log Management

**Current Implementation**: Simple file-based logging.

**Potential Enhancements**:
- Log rotation to prevent disk exhaustion
- Structured logging (JSON format)
- Log level filtering
- Centralized log aggregation

---

## 4. `/app/__pycache__/`: Python Bytecode Cache

### 4.1 Purpose

Python bytecode cache directory containing `.pyc` files.

### 4.2 Generation Mechanism

Python automatically compiles `.py` files to bytecode on first import:
```
script.py → __pycache__/script.cpython-311.pyc
```

### 4.3 Operational Impact

**Performance**: Eliminates recompilation on subsequent imports.

**Storage**: Typically 10-20% of source file size.

**Exclusion**: Should be excluded from version control (`.gitignore`).

---

## 5. Inter-Directory Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        /app/                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ browser_    │  │ pdf-viewer/ │  │ data/       │             │
│  │ guard.py    │──│ (extension) │──│ chrome_data/│             │
│  │             │  │             │  │ (profile)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                                        │              │
│         │         ┌─────────────┐                │              │
│         └────────▶│ logs/       │◀───────────────┘              │
│                   │ chromium.log│                               │
│                   └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### 5.1 Data Flow

1. `browser_guard.py` launches Chromium with `--load-extension=/app/pdf-viewer`
2. Chromium uses `/app/data/chrome_data/` as user profile
3. Browser logs written to `/app/logs/chromium.log`
4. PDF viewer extension intercepts PDF URLs and renders with PDF.js

---

## 6. Security Analysis

### 6.1 Chrome Profile Data (`/app/data/chrome_data/`)

**Risk Level**: Medium-High

**Sensitive Data**:
- `Cookies`: Session tokens
- `Login Data`: Saved passwords (encrypted)
- `History`: Browsing patterns
- `Web Data`: Autofill information

**Mitigations**:
- Profile isolation per session
- Regular cleanup of sensitive data
- Encryption for password storage

### 6.2 PDF Viewer Extension (`/app/pdf-viewer/`)

**Risk Level**: Low

**Permissions**:
- `storage`: Local settings
- `scripting`: Content script injection
- `host_permissions: <all_urls>`: Universal URL access

**Assessment**: Standard PDF viewer permissions; no elevated privileges.

### 6.3 Log Files (`/app/logs/`)

**Risk Level**: Low

**Considerations**:
- May contain URL fragments
- Could include error messages with sensitive data
- Regular rotation recommended

---

*Document Version: 1.0*
*Analysis Date: 2026-01-31*
