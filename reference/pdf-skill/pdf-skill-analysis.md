# The PDF Skill

The pdf skill handles PDF creation and processing through a multi-route architecture. Unlike other skills that use a single toolchain, PDF generation requires different approaches depending on the document type: HTML+Paged.js for business documents, LaTeX+Tectonic for academic papers, and pikepdf for existing PDF manipulation.

---

## Multi-Route Architecture

The skill selects routes based on document requirements:

**HTML Route** (Primary): Uses Playwright + Paged.js for business documents. Best for reports with complex layouts, charts, and visual design.

**LaTeX Route**: Uses Tectonic compiler for academic papers. Best for mathematical content, citations, and formal academic formatting.

**Process Route**: Uses pikepdf + pdfplumber for existing PDF operations. Best for form filling, page manipulation, content extraction.

**Convert Route**: Uses LibreOffice for Office format conversion.

---

## HTML Route

The HTML route is the default and most complex. It uses `html_to_pdf.js`, a ~600 line Node.js script that orchestrates the conversion.

The conversion pipeline:

```
Input HTML
    │
    ▼
Load & Inject Playwright ──→ Custom CSS (optional)
    │
    ▼
Detect Counters ──→ Warn if CSS counters used
Detect Mermaid ──→ Wait for SVG rendering
Detect KaTeX ──→ Trigger math rendering
    │
    ▼
Fix Counters ──→ Burn in counter values
Fix Tall Elements ──→ Remove page-break-inside
    │
    ▼
Inject Paged.js ──→ Local bundle or CDN
    │
    ▼
Wait for Pages ──→ Poll until count stable
    │
    ▼
Detect Overflow ──→ Warn if elements overflow
Get Statistics ──→ Word count, figures, tables
Detect Anomalies ──→ Blank/low-content pages
    │
    ▼
Export PDF (scale=1.5 workaround)
```

The `html_to_pdf.js` script includes several critical workarounds:

**CSS Counter Detection**: Paged.js reorders DOM during pagination, breaking CSS counters. The script detects counter usage and warns users to use `data-*` attributes instead.

```javascript
// Detect counter-reset, counter-increment, content: counter()
const counterWarnings = await page.evaluate(() => {
    const warnings = [];
    const styles = document.querySelectorAll('style');
    styles.forEach((style, idx) => {
        const css = style.textContent || '';
        const counterResetMatches = css.match(/[^@]counter-reset\s*:\s*([^;]+)/gi);
        const counterIncMatches = css.match(/counter-increment\s*:\s*([^;]+)/gi);
        if (/content\s*:\s*[^;]*counter\s*\(/i.test(css)) {
            // ... warn
        }
    });
    return warnings;
});
```

**Counter Fix (Burn-in)**: Before Paged.js runs, the script "burns in" counter values as data attributes.

```javascript
const counterFixCount = await page.evaluate(() => {
    let fixedCount = 0;
    const olLists = document.querySelectorAll('ol');
    olLists.forEach(ol => {
        const liItems = ol.querySelectorAll(':scope > li');
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

**Mermaid Rendering Wait**: The script waits for Mermaid diagrams to render before pagination.

```javascript
const hasMermaid = await page.evaluate(() => {
    return document.querySelectorAll('.mermaid').length > 0;
});

if (hasMermaid) {
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

**Pagination Stability Detection**: The script waits for the page count to stabilize.

```javascript
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

**PDF Export Scale Workaround**: The script uses `scale: 1.5` to fix a page filling issue where content renders at ~67% size without it.

```javascript
await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    tagged: true,
    scale: 1.5  // Critical workaround
});
```

---

## Critical Constraints

The HTML route has strict limitations:

- **Paged.js Loading**: Conversion script injects automatically — **DO NOT** duplicate
- **JS Chart Libraries**: **PROHIBITED** — ECharts, Chart.js, D3.js, Plotly cause layout conflicts
- **Data Charts**: Use `<img>` with pre-generated matplotlib PNG
- **Mermaid Layout**: Default to `flowchart LR` — `TB` risks overflow
- **Mermaid Nodes**: ≤12 total, ≤3 subgraphs, ≤5 nodes per subgraph
- **CSS Counters**: **PROHIBITED** — Paged.js DOM reordering breaks counters

---

## Cover Design Requirements

Full-bleed covers require all three CSS rules:

```css
body { margin: 0; padding: 0; }                    /* Reset browser default */
@page :first { margin: 0; }                        /* Remove page margin */
.cover { margin: 0; position: relative;            /* Element positioning */
         width: 210mm; height: 297mm; overflow: hidden; }
```

---

## LaTeX Route

The LaTeX route uses the Tectonic compiler (57.4MB binary), a modern LaTeX engine that auto-downloads packages.

Compilation uses a Python wrapper:

```python
python3 /app/.kimi/skills/pdf/scripts/compile_latex.py main.tex --runs 2
```

The wrapper provides:
- Log filtering (removes noise)
- Multiple compilation passes
- PDF statistics extraction
- Error/warning categorization

Log filtering removes verbose output:

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

Issue categorization:
- Errors: `^error:` — Critical
- Warnings: `^warning:` — Medium
- Layout: `Overfull/Underfull \[hv]box` — Medium
- Fonts: `Font shape|Missing character` — Low

Package loading order matters:

```latex
% Required base packages
\usepackage{graphicx, xcolor, geometry, amsmath}

% ... other packages ...

% hyperref MUST be loaded LAST
\usepackage[colorlinks=true, linkcolor=blue, citecolor=darkgray,
            urlcolor=blue, bookmarks=true, unicode=true]{hyperref}
```

---

## Process Route

The Process route uses pikepdf and pdfplumber for existing PDF manipulation.

```python
pdf.py <command> <subcommand> [options]
```

Commands:
- `form info/fill` — Form field inspection and filling
- `extract text/table/image` — Content extraction
- `pages merge/split/rotate/crop` — Page operations
- `meta get/set` — Metadata operations
- `convert` — Format conversion

Output format is JSON:

```json
// Success
{"status": "success", "data": {...}}

// Error
{"status": "error", "error": "ErrorType", "message": "...", "hint": "..."}
```

Exit codes:
- 0: Success
- 1: Argument error
- 2: File not found
- 3: PDF parse error
- 4: Operation failed

---

## Paged.js Library

The skill includes a bundled copy of Paged.js (922KB, version 0.4.3) for offline operation. This avoids CDN dependencies and ensures version stability.

Key features:
- `@page` rule processing
- Page break control (`page-break-before`, `page-break-after`, `page-break-inside`)
- Running headers/footers (`@top-center`, `@bottom-center`)
- Named pages (`page: cover`)
- Page number counters (`counter(page)`)

---

## PDF Viewer Extension

The PDF skill is separate from the PDF Viewer Chrome extension at `/app/pdf-viewer/`. The extension is for viewing PDFs in the browser; the skill is for creating and processing PDFs. They don't share code directly.

---

## File Inventory

The pdf skill contains 17 files:
- `SKILL.md` — Route selection and principles
- `routes/html.md` — HTML+Paged.js route documentation
- `routes/latex.md` — LaTeX+Tectonic route documentation
- `routes/process.md` — Existing PDF operations documentation
- `scripts/html_to_pdf.js` (~600 lines) — Main conversion engine
- `scripts/paged.polyfill.js` (922KB) — Paged.js library
- `scripts/compile_latex.py` (~350 lines) — LaTeX wrapper
- `scripts/pdf.py` (~260 lines) — Unified CLI entry
- `scripts/browser_helper.js` — Playwright utilities
- `scripts/cmd_*.py` — Form, extract, pages, meta, convert commands
