# HTML to PDF Route

Create professional PDFs using HTML + Playwright + Paged.js.

---

## Step 0: Check & Install Dependencies (Do First)
**Run immediately before writing HTML**—package download takes time.

```bash
/app/.kimi/skills/pdf/scripts/setup.sh
```

The script only checks status, does not auto-install. If missing, install manually:
- Node.js: `brew install node` (macOS) / `apt install nodejs` (Ubuntu)
- Playwright: `npm install -g playwright && npx playwright install chromium`

Run in background while writing HTML.

## Step 1: Write HTML
1. **Do NOT load Paged.js**: The conversion script injects it automatically; duplicate loading causes page count doubling and layout corruption.
2. **Diagrams and Charts**:
   - **Use Mermaid** for flowcharts, sequence diagrams, architecture diagrams (renders as static SVG; must set `theme:'neutral'`)
   - **Use `<img>` tags** for data charts (bar, line, pie) — pre-generate with matplotlib
   - **Prohibited**: ECharts, Chart.js, D3.js, Plotly, or any JS charting library that renders dynamically — causes layout conflicts with Paged.js pagination
   - **Chart size rule**: Always use **landscape figsize** (width > height), e.g., `figsize=(10, 6)`. Never use square or portrait. This prevents charts from overflowing the page.

## Step 2: Convert to PDF
```bash
node /app/.kimi/skills/pdf/scripts/html_to_pdf.js document.html
node /app/.kimi/skills/pdf/scripts/html_to_pdf.js document.html --output output.pdf
```
After conversion, the script outputs:
- Page count, word statistics, figures/tables count
- **Overflow detection**: Warns if any `pre`, `table`, `figure`, `img`, etc. overflows page width
- **CSS Counter detection**: Warns if CSS counters are used (will break with Paged.js)
- Anomalous pages detection (blank, low-content)

If overflow is detected, add `max-width: 100%` to the offending element.

---

## Design Principles

### LaTeX Academic Style (Default)
Default output should approximate LaTeX academic paper style, not web/UI style.

#### Prohibited UI Components
| Prohibited | Alternative |
|------------|-------------|
| Card components (bordered + header) | Three-line tables or plain paragraphs |
| Statistics dashboards (number card grids) | Tables for data display |
| Dark title bars | Bold titles + thin border or left border |
| Timeline components | Numbered lists or tables |
| Dark-themed code blocks | Light gray background `#f5f5f5` |
| Rounded borders | Square or no borders |
| Shadow effects | No shadows |

#### LaTeX-Style Patterns
**Theorem/Definition boxes** (left border, not dark title bar):
```css
.theorem {
    border-left: 3px solid #333;
    padding-left: 1em;
    margin: 1em 0;
}
.theorem-title { font-weight: bold; }
.theorem-content { font-style: italic; }
```

**Algorithm boxes** (thin border + white background):
```css
.algorithm {
    border: 1px solid #333;
    padding: 0.5em;
    background: white;
}
```

#### Color Standards
**Body/Content**: `#333` text, `#f5f5f5` code/table background, grayscale palette.
**Cover**: Depends on document type (see below).

#### Icons and Emoji
**PROHIBITED** (unless user explicitly requests): Do NOT use emoji or decorative icons. Emoji fails on Linux (missing fonts), and icons often look unprofessional in formal documents. Use plain text instead.

---

### Cover Design

#### Style Selection
| Style | Characteristics | When to Use |
|-------|-----------------|-------------|
| **Minimal** | White background, centered layout, no decoration | Default for academic; safe and professional |
| **Designed** | CSS gradients/geometric shapes, modern typography, top-tier 2024 designer aesthetic | When visual impact is needed |

**Default to Minimal for academic contexts, but not mandatory.** Choose based on document tone and user preference.

#### CRITICAL: Cover CSS Requirements
All cover types MUST include these CSS rules to ensure full-bleed cover (no white borders):
```css
/* 1. REQUIRED: Reset browser default margin (prevents 8px white border) */
body {
    margin: 0;
    padding: 0;
}

/* 2. REQUIRED: Remove page margin for cover */
@page :first { margin: 0; }

/* 3. REQUIRED: Cover element setup */
.cover {
    width: 210mm;
    height: 297mm;
    margin: 0;               /* Explicit zero margin */
    position: relative;      /* Required for proper positioning */
    overflow: hidden;        /* Prevent content overflow */
    page-break-after: always;
}
```

**Why all three are needed:**
| Rule | What it does | Without it |
|------|--------------|------------|
| `body { margin: 0; }` | Removes browser default 8px margin | Thin white border on left/top edges |
| `@page :first { margin: 0; }` | Removes CSS page margin | Cover offset/cropped by page margins |
| `.cover { margin: 0; }` | Ensures cover element has no margin | Potential gaps from inherited styles |

**Common mistake**: Only setting `@page :first { margin: 0; }` but forgetting `body { margin: 0; }` — this causes the "thin white border on left/top, large gap on right/bottom" symptom.

#### Minimal Cover
```html
<div class="cover">
    <div class="cover-content">
        <h1 class="cover-title">Document Title</h1>
        <p class="cover-subtitle">Subtitle or Document Type</p>
        <div class="cover-meta">
            <p>Author Name</p>
            <p>Institution</p>
            <p>Date</p>
        </div>
    </div>
</div>
```
```css
.cover { background: white; position: relative; margin: 0; }
.cover-content { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; width: 80%; }
.cover-title { font-size: 28pt; font-weight: 700; color: #333; margin-bottom: 0.5cm; }
.cover-subtitle { font-size: 16pt; color: #666; margin-bottom: 3cm; }
.cover-meta { font-size: 12pt; color: #333; line-height: 2; }
```
**Constraints**: No gradients, shadows, rounded cards, or decorative elements.

#### Designed Cover
Cover background is what separates "acceptable" from "impressive". Plain text cover = mediocre delivery.

**Design Principles**:
- Background should have **center whitespace** for title, decorations at edges/corners
- Use **low-saturation colors**, avoid clashing with content
- Implement with pure CSS (gradients, shapes, pseudo-elements)

**Style Reference** (choose based on document context, DO NOT copy verbatim—create original designs):

| Style | Key Elements | Use Case |
|-------|--------------|----------|
| Muji | Thin borders + corner squares + ample whitespace | Minimalist, Japanese, lifestyle |
| Bauhaus | Scattered geometric shapes (circles, triangles, rectangles) | Art, design, creative |
| Swiss | Grid lines + corner blocks + accent bars | Professional, corporate, rigorous |
| Soft Blocks | Soft-colored rectangles, overlapping with transparency | Warm, education, healthcare |
| Rounded Geometric | Rounded rectangles, pill shapes | Tech, internet, youthful |
| Frosted Glass | Blur + transparency + subtle borders | Modern, premium, tech |
| Gradient Ribbons | Soft gradient ellipses + small dots | Feminine, beauty, gentle |
| Dot Matrix | Regular dot/grid patterns | Technical, data, engineering |
| Double Border | Nested borders + corner decorations | Traditional, formal, legal |
| Waves | Bottom SVG waves + gradient background | Ocean, eco, fluidity |
| Warm Natural | Earth tones + organic shapes | Environmental, agriculture, nature |

**CSS Techniques**:
- Geometric shapes: `position: absolute` + `width/height` + `background` or `border`
- Gradients: `radial-gradient()`, `linear-gradient()` with low saturation
- Decorative elements: `::before`, `::after` pseudo-elements
- Transparency: `rgba()` or `opacity` for layering
- Waves: SVG `<path>` or CSS `clip-path`

#### Background Image (if needed)
If using an image instead of CSS, **do NOT use CSS `background-image`** — it breaks in Paged.js due to DOM restructuring.

**Must use `<img>` + absolute positioning**:
```html
<div class="cover">
    <img class="cover-bg" src="image.jpg" alt="">
    <div class="cover-content">...</div>
</div>
```
```css
.cover-bg {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    object-fit: cover; object-position: center; z-index: 0;
}
.cover-content {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: 1; text-align: center; width: 80%;
    color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
}
```
**Why?** Paged.js restructures DOM into `.pagedjs_page → .pagedjs_sheet → .pagedjs_area → .pagedjs_page_content`, breaking CSS backgrounds. `<img>` with `position: absolute` ensures full-page coverage.

#### Typography Standards
- **Fonts**: Serif preferred (Georgia, "Noto Serif SC")
- **Font sizes**: Body 11pt, subheadings 14pt, headings 18-20pt
- **Line height**: 1.5-1.6
- **Alignment**: If using `text-align: justify`, **must** add `text-align-last: left` to prevent short lines from stretching character spacing

---

## Paged.js Pagination Features

### @page Rules
```css
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @top-center { content: string(doctitle); }
    @bottom-center { content: counter(page); }
}
@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

/* Named pages: hide header/footer on cover and TOC (supports multi-page) */
@page cover { @top-center { content: none; } @bottom-center { content: none; } }
@page toc { @top-center { content: none; } @bottom-center { content: none; } }
.cover { page: cover; }
.toc-page { page: toc; }

/* CRITICAL: Prevent "undefined" in header before h1 appears */
body { string-set: doctitle ""; }
h1 { string-set: doctitle content(); }
```

### Key Properties
| Property | Purpose |
|----------|---------|
| `string-set: doctitle ""` | Set on body, empty default to prevent "undefined" |
| `string-set: doctitle content()` | Set on h1, updates header with actual title |
| `page: cover` / `page: toc` | Assign element to named page (hides header/footer) |
| `page-break-after: always` | Force page break |
| `page-break-inside: avoid` | Prevent tables/figures from breaking |
| `page-break-after: avoid` | Prevent heading-content separation |
| `orphans: 2; widows: 2` | Control orphan lines |

**`page-break-inside: avoid` principle**: Only use on small atomic components; large containers cause entire blank pages.
```css
/* Correct: Only protect small components */
figure, .theorem, .algorithm { page-break-inside: avoid; }
tr { page-break-inside: avoid; }  /* Single row doesn't break */

/* Wrong: Large containers cause blank pages */
.section, .chapter { page-break-inside: avoid; }

/* Repeat table headers across pages */
thead { display: table-header-group; }
```

**Unexpected blank pages?** Common causes: `page-break-after: always` after cover or consecutive `page-break`. Solution: Use CSS selectors for pagination (e.g., `.abstract:first-of-type { page-break-before: always; }`) instead of explicit `<div class="page-break">`.

### Advanced TOC (with Page Numbers)
Use `target-counter()` for TOC with page numbers and leader dots:
```css
.toc a::after {
    content: leader('.') target-counter(attr(href url), page);
}
```
TOC items **must** be `<a href="#section-id">`, not plain text.

### Cross-reference Page Numbers
```css
a.pageref::after {
    content: target-counter(attr(href url), page);
}
```

---

## Math Formulas (KaTeX)
Include KaTeX CSS and JS, use auto-render extension for automatic rendering of `$...$` (inline) and `$$...$$` (block).

**Colors**: Formulas default to black `#333`, **no** color highlighting.
**Equation numbering**: Use flex layout + `data-*` attributes for right-side numbering (CSS counter breaks with Paged.js).
**Note**: Conversion script automatically triggers KaTeX rendering. If source code still shows, check CDN accessibility and don't wrap `renderMathInElement` in `DOMContentLoaded`.

---

## Diagrams (Mermaid)

### CRITICAL: Height Constraint
**Mermaid SVG that exceeds page height will break Paged.js pagination**, causing "undefined" errors and blank pages.

**Layout Selection (MUST follow)**:
| Layout | When to Use | Height Risk |
|--------|-------------|-------------|
| `flowchart LR` | **Default choice** - horizontal flow | Low |
| `flowchart TB` | Only for very simple diagrams (≤6 nodes, no subgraph) | High |

**Complexity Limits**:
| Constraint | Limit | Reason |
|------------|-------|--------|
| Subgraphs | ≤ 3 | Each subgraph adds vertical height |
| Nodes per subgraph | ≤ 5 | Prevents overflow |
| Total nodes | ≤ 12 | Keeps diagram compact |
| `<br>` in node text | Avoid | Increases node height |

### Configuration
```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'neutral',  // Required!
    themeVariables: {
        primaryColor: '#f5f5f5',
        primaryTextColor: '#333',
        primaryBorderColor: '#999',
        lineColor: '#666'
    }
});
```

### Prohibited
- **Themes**: `default` (too blue), `forest` (high saturation), `dark`
- **Beta features**: `xychart-beta`, etc.
- **`flowchart TB` with >6 nodes or any subgraph**

### Complex Diagrams: Use Tables Instead
For "technical roadmap", "research framework", "system architecture" with many steps:

**DON'T**: Single complex Mermaid with 6 subgraphs
**DO**: Table + simplified Mermaid

```html
<!-- Table for details + simple Mermaid for overview -->
<table>
<caption data-label="Table X">Technical Roadmap Phases</caption>
<thead><tr><th>Phase</th><th>Tasks</th><th>Output</th></tr></thead>
<tbody>
<tr><td>Data Collection</td><td>Crawl reviews, gather sales</td><td>Raw database</td></tr>
<tr><td>Data Processing</td><td>Clean, tokenize, label</td><td>Labeled dataset</td></tr>
...
</tbody>
</table>

<div class="mermaid">
flowchart LR
    A[Collection] --> B[Processing] --> C[Training] --> D[Evaluation]
</div>
```

### Debugging
If PDF shows "undefined" or blank pages around diagrams:
1. Diagram too tall → Switch to `flowchart LR`
2. Too many subgraphs → Reduce to ≤3 or use table
3. Still failing → Replace with table entirely

---

## Professional Components
Use these components appropriately for more complete, professional documents.

### Academic Essentials
| Component | Use Case | Key Points |
|-----------|----------|------------|
| **Three-line tables** | Data display | Booktabs style: thick lines above/below `thead/tbody`, no vertical lines; **add `max-width: 100%`** |
| **Figure/table numbering** | Figure/table captions | **Use `data-*` attributes** (CSS Counter breaks with Paged.js) |
| **Equation numbering** | Math formulas | **Use `data-*` attributes**, right-side (2-1) format |
| **Section numbering** | Section headings | **Write manually** or use `data-*` attributes |
| **Cross-references** | Reference figures/tables/equations/sections | **Must use `<a href="#id">`**, `id` at container top |
| **Table of contents** | Section navigation | **TOC items must be `<a href="#section-id">`** for clickability |
| **Lists of figures/tables** | Figure/table directories | Same as above, separate page listing all figures/tables |
| **References** | Academic citations | Write manually, black superscript style |
| **Footnotes** | Supplementary notes | Paged.js specific syntax `float: footnote` |

### Layout Enhancements
| Component | Use Case | Key Points |
|-----------|----------|------------|
| **Two-column layout** | Academic papers | `column-count: 2`, span columns with `column-span: all` |
| **Drop caps** | Chapter openings | `::first-letter` + `float: left`, enhances aesthetics |
| **Code highlighting** | Code display | Prism.js, **must use light theme** `#f5f5f5` |
| **Appendices** | Supplementary material | A, B, C letter numbering, write manually |

### Auto-numbering Standards
| Type | Method | Notes |
|------|--------|-------|
| Sections | Write manually | Linear writing less error-prone |
| Figures/tables/equations | **`data-*` attributes** | CSS Counter is broken by Paged.js DOM reordering |
| References | Write manually | Must be real, must verify via search |

#### Why Not CSS Counter?
**PROHIBITED**: Do NOT use `counter-reset`, `counter-increment`, or `content: counter(...)` anywhere in CSS. This includes custom step lists, numbered badges, or any decorative numbering.

Paged.js reorders DOM during pagination, which breaks CSS counters. Common symptoms:
- All numbers show as 0 (e.g., "Figure 0", "Table 0", "Step 0")
- Numbers reset unexpectedly mid-document

**Always write numbers explicitly** in HTML or use `data-*` attributes.

#### Recommended: `data-*` Attributes
```html
<!-- Figures -->
<figure id="fig-1">
    <img src="chart.png" alt="...">
    <figcaption data-label="Figure 1">System Architecture</figcaption>
</figure>

<!-- Tables -->
<table>
    <caption data-label="Table 1">Performance Comparison</caption>
    ...
</table>

<!-- Equations -->
<div class="equation" data-label="(1)">
    $$E = mc^2$$
</div>
```

```css
figcaption::before { content: attr(data-label) "  "; font-weight: bold; }
caption::before { content: attr(data-label) "  "; font-weight: bold; }
.equation::after { content: attr(data-label); float: right; }
```

**Anchor placement**: `id` goes on `<figure>` not `<figcaption>`, for correct jump positioning.

#### Prevent Overflow (CRITICAL)
**All block elements must not exceed page width.** Use this unified rule:
```css
/* Prevent all block elements from overflowing page */
pre, table, figure, img, svg, .mermaid, blockquote, .equation {
    max-width: 100%;
    box-sizing: border-box;
}
pre { overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
figure img, figure svg { max-width: 80%; max-height: 40vh; height: auto; }
table { overflow-x: auto; }

/* Prevent justify from stretching short lines */
body { text-align: justify; text-align-last: left; }

/* Prevent long URLs from overflowing */
a { word-break: break-all; }

/* Prevent long formulas from overflowing */
.katex-display { overflow-x: auto; }

/* Prevent long code/words from overflowing */
code { word-break: break-word; }

/* Prevent table rows from breaking mid-cell */
tr { page-break-inside: avoid; }
```
The conversion script auto-detects overflow and warns. Fix any reported elements.

#### Vertical Centering (CRITICAL)
**PROHIBITED**: Do NOT use `line-height` or `vertical-align: middle` for centering text in fixed-size containers. These depend on font baseline and are unreliable—text often appears off-center.

**Required**: Use flexbox. This applies to ALL fixed-size containers with centered content: step numbers, badges, tags, avatar placeholders, icon wrappers, etc.

```css
/* WRONG - text shifts with different fonts */
.step-number {
    width: 1.5em; height: 1.5em;
    line-height: 1.5em;
    text-align: center;
}

/* CORRECT - universal pattern for any centered container */
.step-number {
    width: 1.5em; height: 1.5em;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
```


### Reference Standards
**All citations must be real, no mocking**—must verify via search, fabricating any author, title, year, or page number is prohibited.

#### Strict Correspondence Constraint
In-text `<a href="#ref-1">[1]</a>` must strictly correspond to end-of-document `<li id="ref-1">`:
- `id` must be unique and matching
- No empty links or dangling references

#### Citation Style (Black Superscript)
```css
a.cite { color: black; text-decoration: none; vertical-align: super; font-size: 0.75em; }
```

#### Hanging Indent (Professional Typesetting Mark)
```css
.references li {
    padding-left: 2em;
    text-indent: -2em;
}
```

#### Citation Format Selection
| Scenario | Format |
|----------|--------|
| Chinese academic papers, coursework | GB/T 7714 (use [J][M][D] etc. document type identifiers) |
| English papers, international journals | APA format |
| Mixed Chinese/English | Chinese uses GB/T 7714, English uses APA |

#### Italics Rules (APA)
Book titles, journal names must be italicized, use `<i>` tag:
```html
<li id="ref-1">Raymond, E. S. (2003). <i>The Art of Unix Programming</i>. Addison-Wesley.</li>
<li id="ref-2">Vaswani, A., et al. (2017). Attention is all you need. <i>NeurIPS</i>, 30, 5998-6008.</li>
```
**Italics scope**: Book titles, Journal names (yes), Article titles, Publishers (no)

### Footnotes (Paged.js Specific Syntax)
```css
.footnote-ref { float: footnote; }
.footnote-ref::footnote-call { content: counter(footnote); vertical-align: super; font-size: 0.75em; }
.footnote-ref::footnote-marker { content: counter(footnote) ". "; }
@page { @footnote { margin-top: 1em; border-top: 1px solid #ccc; padding-top: 0.5em; } }
```
```html
Body text<span class="footnote-ref">This is footnote content, automatically typeset at page bottom</span>.
```

### Table of Contents (Must Use Links for Clickability)
```html
<!-- Correct: Use <a> links -->
<ul class="toc">
    <li><a href="#sec1">1. Introduction</a></li>
    <li><a href="#sec2">2. Methods</a></li>
</ul>

<!-- Wrong: Plain text not clickable -->
<div class="toc-item">1. Introduction</div>
```
```css
/* TOC item: title + leader dots + auto page number */
.toc a::after {
    content: leader('.') target-counter(attr(href url), page);
}
```
**Wrong page numbers?** Use `target-counter()` instead of hardcoded page numbers; Paged.js calculates automatically.

### CJK Fonts
Server needs CJK fonts installed or use web fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC&display=swap" rel="stylesheet">
```

### RTL Languages (Arabic, Persian, Hebrew)
```html
<html dir="rtl" lang="fa">
```
```css
body { direction: rtl; text-align: right; }
.toc a { display: flex; flex-direction: row-reverse; }
```
**Note**: Paged.js has limited support for RTL `leader('.')`. TOC may need table layout instead.

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `html_to_pdf.js` | HTML to PDF (Playwright + Paged.js), includes page/word count and anomaly detection |

## Tech Stack

| Library | Purpose | License |
|---------|---------|---------|
| Playwright | Browser automation | Apache-2.0 |
| Paged.js | CSS Paged Media polyfill | MIT |
| KaTeX | Math formula rendering | MIT |
| Mermaid | Diagram rendering | MIT |

---

## Important Notes

### Resource Requirements
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 1 GB | 2+ GB |
| Disk | 500 MB (Chromium) | 1 GB |

**Chromium memory**: ~200-500MB per conversion. For large documents (50+ pages), expect higher usage.

### Large Document Strategy
For documents exceeding 50 pages:
1. **Split into sections**: Write separate HTML files, merge PDFs afterward
2. **Reduce complexity**: Fewer Mermaid diagrams, simpler tables
3. **Increase timeout**: Default 120s may not suffice

### Offline Operation
The conversion script bundles Paged.js locally (`paged.polyfill.js`). However:
- **KaTeX**: Requires CDN or local bundle
- **Mermaid**: Requires CDN or local bundle
- **Web fonts**: Require network or local installation

For fully offline operation, include KaTeX/Mermaid JS/CSS in your HTML file directly.

### Common Failure Modes
| Symptom | Cause | Solution |
|---------|-------|----------|
| Blank PDF | Paged.js timeout | Simplify content, increase timeout |
| "undefined" in PDF | Mermaid too tall | Use `flowchart LR`, reduce nodes |
| Missing fonts | CJK not installed | Install fonts or use web fonts |
| Truncated content | Element overflow | Add `max-width: 100%` |
| Numbers show as 0 | CSS Counter broken by Paged.js | Use `data-*` attributes or write numbers explicitly |
| Text off-center in circles | `line-height` centering unreliable | Use `display: inline-flex` + `align-items/justify-content: center` |
