# PDF Scripts Analysis
## `/app/.kimi/skills/pdf/scripts/` — PDF Generation and Processing Tools

---

## Executive Summary

The `scripts/` directory contains 13 files implementing the PDF skill's multi-route architecture. These scripts handle HTML-to-PDF conversion (via Playwright + Paged.js), LaTeX compilation (via Tectonic), and existing PDF manipulation (via pikepdf/pdfplumber).

---

## 1. File Inventory

| File | Type | Size | Purpose |
|------|------|------|---------|
| `html_to_pdf.js` | Node.js | ~600 lines | Main HTML→PDF conversion engine |
| `paged.polyfill.js` | Library | 922KB | Paged.js pagination library (bundled) |
| `browser_helper.js` | Node.js | ~100 lines | Playwright browser detection |
| `compile_latex.py` | Python | ~350 lines | LaTeX compilation wrapper |
| `pdf.py` | Python | ~260 lines | Unified CLI entry point |
| `pdf.sh` | Shell | ~80 lines | Shell wrapper |
| `setup.sh` | Shell | ~50 lines | Dependency checker |
| `package.json` | JSON | ~30 lines | Node.js dependencies |
| `cmd_convert.py` | Python | ~100 lines | Office→PDF conversion |
| `cmd_extract.py` | Python | ~150 lines | Text/table/image extraction |
| `cmd_form.py` | Python | ~120 lines | Form filling |
| `cmd_meta.py` | Python | ~80 lines | Metadata operations |
| `cmd_pages.py` | Python | ~150 lines | Merge/split/rotate/crop |

---

## 2. html_to_pdf.js — HTML to PDF Conversion Engine

### 2.1 Architecture

```
Input HTML
    │
    ▼
┌─────────────────┐
│  Load & Inject  │──→ Custom CSS (optional)
│  Playwright     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Detect Counters │──→ Warn if CSS counters used
│ Detect Mermaid  │──→ Wait for SVG rendering
│ Detect KaTeX    │──→ Trigger math rendering
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Fix Counters    │──→ Burn in counter values
│ Fix Tall Elt    │──→ Remove page-break-inside
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Inject Paged.js │──→ Local bundle or CDN
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Wait for Pages  │──→ Poll until count stable
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Detect Overflow │──→ Warn if elements overflow
│ Get Statistics  │──→ Word count, figures, tables
│ Detect Anomalies│──→ Blank/low-content pages
└─────────────────┘
    │
    ▼
Export PDF (scale=1.5 workaround)
```

### 2.2 Key Features

#### CSS Counter Detection

```javascript
// Detect counter-reset, counter-increment, content: counter()
const counterWarnings = await page.evaluate(() => {
    const warnings = [];
    const styles = document.querySelectorAll('style');
    
    styles.forEach((style, idx) => {
        const css = style.textContent || '';
        
        // Check for counter-reset (excluding @page)
        const counterResetMatches = css.match(/[^@]counter-reset\s*:\s*([^;]+)/gi);
        // Check for counter-increment
        const counterIncMatches = css.match(/counter-increment\s*:\s*([^;]+)/gi);
        // Check for content: counter()
        if (/content\s*:\s*[^;]*counter\s*\(/i.test(css)) {
            // ... warn
        }
    });
    
    return warnings;
});
```

**Why This Matters**: Paged.js reorders DOM during pagination, breaking CSS counters. The script warns users to use `data-*` attributes instead.

#### Counter Fix (Burn-in)

```javascript
// "Burn in" counter values as data attributes before Paged.js runs
const counterFixCount = await page.evaluate(() => {
    let fixedCount = 0;
    const olLists = document.querySelectorAll('ol');
    
    olLists.forEach(ol => {
        const liItems = ol.querySelectorAll(':scope > li');
        
        // Check if using custom numbering
        const hasCustomNumbering = computedStyle.listStyleType === 'none';
        
        if (hasCustomNumbering) {
            ol.setAttribute('data-counter-fixed', 'true');
            liItems.forEach((li, index) => {
                li.setAttribute('data-counter', index + 1);
                fixedCount++;
            });
        }
    });
    
    // Inject CSS to use data-counter
    const style = document.createElement('style');
    style.textContent = `
        ol[data-counter-fixed] { counter-reset: none !important; }
        ol[data-counter-fixed] > li::before {
            content: "[" attr(data-counter) "] " !important;
        }
    `;
    document.head.appendChild(style);
    
    return fixedCount;
});
```

#### Mermaid Rendering Wait

```javascript
const hasMermaid = await page.evaluate(() => {
    return document.querySelectorAll('.mermaid').length > 0;
});

if (hasMermaid) {
    console.log('Waiting for Mermaid diagrams to render...');
    await page.waitForFunction(() => {
        const mermaids = document.querySelectorAll('.mermaid');
        for (const m of mermaids) {
            if (!m.querySelector('svg') && !m.getAttribute('data-processed')) {
                return false;
            }
        }
        return true;
    }, { timeout: 30000 });
    await delay(2000);  // Stabilization time
}
```

#### KaTeX Rendering

```javascript
const katexStatus = await page.evaluate(() => {
    const hasKatexLib = typeof renderMathInElement === 'function' || typeof katex !== 'undefined';
    const hasRenderedKatex = document.querySelectorAll('.katex').length > 0;
    const hasUnrenderedMath = /\$[^$]+\$/.test(document.body.innerText);
    return { hasKatexLib, hasRenderedKatex, hasUnrenderedMath };
});

if (katexStatus.hasKatexLib && !katexStatus.hasRenderedKatex && katexStatus.hasUnrenderedMath) {
    await page.evaluate(() => {
        renderMathInElement(document.body, {
            delimiters: [
                {left: "$$", right: "$$", display: true},
                {left: "$", right: "$", display: false}
            ],
            throwOnError: false
        });
    });
    await delay(1000);
}
```

#### Paged.js Integration

```javascript
// Prefer local bundle, fallback to CDN
const pagedJsLocal = path.join(__dirname, 'paged.polyfill.js');
if (fs.existsSync(pagedJsLocal)) {
    const pagedJsContent = fs.readFileSync(pagedJsLocal, 'utf-8');
    await page.addScriptTag({ content: pagedJsContent });
} else {
    await page.addScriptTag({
        url: 'https://unpkg.com/pagedjs@0.4.3/dist/paged.polyfill.js'
    });
}
```

#### Pagination Stability Detection

```javascript
// Wait for page count to stabilize (no change for 3 consecutive checks)
let lastPageCount = 0;
let stableCount = 0;
const maxWaitTime = 120000;  // 2 minutes max

while (stableCount < 3) {
    if (Date.now() - startTime > maxWaitTime) {
        console.log('Warning: Pagination timeout');
        break;
    }
    
    await delay(1000);
    const currentPageCount = await page.evaluate(() =>
        document.querySelectorAll('.pagedjs_page').length
    );
    
    if (currentPageCount === lastPageCount) {
        stableCount++;
    } else {
        stableCount = 0;
        lastPageCount = currentPageCount;
        console.log(`  Pagination in progress: ${currentPageCount} pages...`);
    }
}
```

#### Overflow Detection

```javascript
const overflows = await page.evaluate(() => {
    const results = [];
    const selectors = 'pre, table, figure, img, svg, .mermaid, blockquote, .equation';
    document.querySelectorAll(selectors).forEach(el => {
        const scrollW = el.scrollWidth;
        const clientW = el.clientWidth;
        if (scrollW > clientW + 2) {  // +2 tolerance
            results.push({
                tag: el.tagName.toLowerCase(),
                class: el.className || '',
                overflow: scrollW - clientW,
                preview: (el.textContent || '').slice(0, 60)
            });
        }
    });
    return results;
});
```

#### PDF Export (Scale Workaround)

```javascript
// WORKAROUND: scale=1.5 fixes page filling issue
// Without this, content renders at ~67% size
// Root cause unclear, appears related to Paged.js internal scaling
await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    tagged: true,
    scale: 1.5  // Critical workaround
});
```

### 2.3 Output Statistics

```
========================
PDF Information
========================
File: document.pdf
Pages: 12
Size: 245.6 KB
Words: ~3,456
Figures/Tables: 5 figures / 3 tables
Path: /mnt/okcomputer/output/document.pdf

========================
Anomaly Detection
========================
  P8: [Low content] 45 words (avg 320, only 14%)
```

---

## 3. compile_latex.py — LaTeX Compilation Wrapper

### 3.1 Purpose

Wraps the Tectonic LaTeX compiler with:
- Log filtering (removes noise)
- Multiple compilation passes
- PDF statistics extraction
- Error/warning categorization

### 3.2 Log Filtering

```python
FILTER_PATTERNS = [
    r'^note: "version 2" Tectonic command-line interface activated',
    r'^note: Running TeX',
    r'^note: Rerunning TeX because',
    r'^note: Running xdvipdfmx',
    r'^note: downloading ',
    r'^note: Skipped writing .* intermediate files',
]
```

### 3.3 Issue Categorization

| Category | Pattern | Severity |
|----------|---------|----------|
| Errors | `^error:` | **Critical** |
| Warnings | `^warning:` | Medium |
| Layout | `Overfull/Underfull \\[hv]box` | Medium |
| Fonts | `Font shape|Missing character` | Low |

### 3.4 PDF Statistics

```python
def extract_pdf_info(pdf_path):
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    
    num_pages = len(reader.pages)
    text = ''.join(page.extract_text() for page in reader.pages)
    word_count = len([w for w in text.split() if w.strip()])
    
    # Count images
    image_count = 0
    for page in reader.pages:
        if '/XObject' in page['/Resources']:
            xobjects = page['/Resources']['/XObject'].get_object()
            for obj in xobjects:
                if xobjects[obj]['/Subtype'] == '/Image':
                    image_count += 1
    
    return num_pages, word_count, image_count
```

---

## 4. pdf.py — Unified CLI Entry

### 4.1 Command Structure

```python
pdf.py <command> <subcommand> [options]
```

| Command | Subcommands | Description |
|---------|-------------|-------------|
| `form` | `info`, `fill` | Form field inspection and filling |
| `extract` | `text`, `table`, `image` | Content extraction |
| `pages` | `merge`, `split`, `rotate`, `crop` | Page operations |
| `meta` | `get`, `set` | Metadata operations |
| `convert` | — | Format conversion |

### 4.2 Output Format

```json
// Success
{"status": "success", "data": {...}}

// Error
{"status": "error", "error": "ErrorType", "message": "...", "hint": "..."}
```

### 4.3 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Argument error |
| 2 | File not found |
| 3 | PDF parse error |
| 4 | Operation failed |

---

## 5. paged.polyfill.js — Paged.js Library

### 5.1 Identity

- **Size**: 922KB (bundled)
- **Version**: 0.4.3
- **License**: MIT
- **Purpose**: CSS Paged Media polyfill for browser-based pagination

### 5.2 Why Bundled?

1. **Offline Operation**: No CDN dependency
2. **Version Stability**: Fixed, tested version
3. **Performance**: Local file load faster than network
4. **Reliability**: Avoids CDN availability issues

### 5.3 Key Features

- `@page` rule processing
- Page break control (`page-break-before`, `page-break-after`, `page-break-inside`)
- Running headers/footers (`@top-center`, `@bottom-center`)
- Named pages (`page: cover`)
- Page number counters (`counter(page)`)

---

## 6. Inter-Script Relationships

```
html_to_pdf.js
    ├── Playwright (browser automation)
    │   └── Chromium
    ├── paged.polyfill.js (pagination)
    └── browser_helper.js (browser detection)

compile_latex.py
    ├── Tectonic (LaTeX compiler)
    └── pypdf (PDF analysis)

pdf.py
    ├── cmd_form.py (pikepdf)
    ├── cmd_extract.py (pdfplumber)
    ├── cmd_pages.py (pikepdf)
    ├── cmd_meta.py (pikepdf)
    └── cmd_convert.py (LibreOffice)
```

---

## 7. Code Metrics

| Script | Lines | Language | Purpose |
|--------|-------|----------|---------|
| html_to_pdf.js | ~600 | Node.js | HTML→PDF conversion |
| compile_latex.py | ~350 | Python | LaTeX compilation |
| pdf.py | ~260 | Python | CLI entry |
| cmd_extract.py | ~150 | Python | Content extraction |
| cmd_pages.py | ~150 | Python | Page operations |
| cmd_form.py | ~120 | Python | Form filling |
| cmd_meta.py | ~80 | Python | Metadata |
| cmd_convert.py | ~100 | Python | Format conversion |
| browser_helper.js | ~100 | Node.js | Browser detection |
| pdf.sh | ~80 | Shell | Wrapper |
| setup.sh | ~50 | Shell | Setup |

---

*Document Version: 1.0*
*Analysis Date: 2026-02-02*
