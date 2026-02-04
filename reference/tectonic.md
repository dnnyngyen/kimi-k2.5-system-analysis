# Tectonic LaTeX Compiler

Tectonic is a modern, self-contained LaTeX compiler based on the XeTeX engine. At 57,402,608 bytes (57.4 MB), this binary provides complete LaTeX compilation capabilities without requiring a full TeX Live installation. It automatically downloads required packages on first use.

---

## Binary Analysis

```bash
$ file /app/tectonic
/app/tectonic: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV),
               dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
               BuildID[sha1]=b14ef99db5d130541d5788c55c3d4faea1cbd00e,
               for GNU/Linux 3.2.0, with debug_info, not stripped
```

- Format: ELF 64-bit LSB PIE (Position Independent Executable)
- Architecture: x86-64
- Size: 57,402,608 bytes (57.4 MB)
- Stripped: No (debug info present)
- Linking: Dynamic
- PIE: Yes (ASLR protection enabled)
- BuildID: b14ef99db5d130541d5788c55c3d4faea1cbd00e

Size breakdown:
- XeTeX Engine: ~20 MB
- Package Index: ~5 MB
- Font Data: ~15 MB
- Support Libraries: ~17 MB

---

## Core Features

**Engine**: XeTeX (Unicode-aware TeX)
**Package Management**: Automatic download on first use
**Font Support**: System fonts, OpenType, TrueType
**Output**: PDF (via xdvipdfmx)
**Cross-references**: Automatic resolution

Tectonic is modern XeTeX—it understands Unicode natively and can use system fonts directly without LaTeX font configuration. This makes it significantly easier to use with non-English languages and custom fonts.

---

## Compilation Workflow

```
.tex Input
    │
    ▼
XeTeX Engine
    │
    ├──► Parse LaTeX
    ├──► Resolve packages (download if needed)
    ├──► Process cross-references
    └──► Generate .xdv (extended DVI)
    │
    ▼
xdvipdfmx
    │
    ▼
PDF Output
```

Tectonic runs XeTeX to generate an extended DVI file, then xdvipdfmx converts that to PDF. The process handles package downloads automatically—if you use a package not present locally, Tectonic fetches it from CTAN.

---

## PDF Skill Integration

The PDF skill uses Tectonic for the LaTeX route:

```
PDF Skill
    │
    ├── HTML Route ──► Playwright + Paged.js
    │
    ├── LaTeX Route ──► compile_latex.py
    │                    │
    │                    └── tectonic
    │                         │
    │                         └── PDF Output
    │
    └── Process Route ──► pikepdf + pdfplumber
```

The `compile_latex.py` wrapper script provides:
- Log filtering (removes noise)
- Multiple compilation passes
- PDF statistics extraction
- Error/warning categorization

Usage:
```bash
# Single compilation
python3 /app/.kimi/skills/pdf/scripts/compile_latex.py main.tex

# Multiple passes (for cross-references)
python3 /app/.kimi/skills/pdf/scripts/compile_latex.py main.tex --runs 2

# With bibliography
python3 /app/.kimi/skills/pdf/scripts/compile_latex.py main.tex --runs 3
```

---

## Package Management

Tectonic maintains a local package cache at `~/.cache/Tectonic/`:
- Downloads packages from CTAN on first use
- Caches for subsequent compilations
- No manual TeX Live installation required

This is the key advantage over traditional LaTeX distributions. Where TeX Live requires a 4+ GB installation upfront, Tectonic starts at 57 MB and fetches only what you need.

---

## Log Filtering

The compile_latex.py wrapper filters verbose Tectonic output:

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

---

## PDF Statistics

The wrapper extracts PDF metadata after compilation:

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

## Comparison with TeX Live

| Aspect | Tectonic | TeX Live |
|--------|----------|----------|
| Size | 57 MB | 4+ GB |
| Installation | Single binary | Complex |
| Package management | Automatic | Manual (tlmgr) |
| Portability | High | Low |
| Offline use | After first download | Full |

Tectonic trades offline capability for size and simplicity. After first use with a given package set, it's fully offline capable. But the initial download requirement means it's not suitable for fully air-gapped environments.

---

## Security Analysis

- Network access: Downloads packages from CTAN
- File system: Reads .tex, writes .pdf
- Execution: Sandboxed by OS
- PIE enabled: Yes (ASLR protection)
- Debug info: Present (not stripped)

The network access is the main security consideration. Tectonic downloads and executes code (LaTeX packages) from the internet. In the Kimi container, this is sandboxed and acceptable. In high-security environments, you'd want to pre-populate the cache.
