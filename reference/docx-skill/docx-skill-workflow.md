# DOCX Skill: Shell and IPython Integration Analysis

## Skill Overview
The DOCX skill handles Word document generation through a dual-stack architecture:
- **Creation**: C# with OpenXML SDK (compiled via shell)
- **Editing**: Python with lxml (via ipython)
- **Validation**: .NET binary validator (via shell)

## Shell Usage Patterns

### 1. Build Orchestration (`./scripts/docx build`)
```bash
# Unified entry point - shell script
cd /app/.kimi/skills/docx/
./scripts/docx build [output.docx]
```

**Internal Pipeline (Shell Commands)**:
```bash
dotnet build                    # Compile C# project
dotnet run -- <output_path>     # Generate .docx
python3 fix_element_order.py    # XML sequence correction
./validator/Validator           # OpenXML schema validation
python3 validate_docx.py        # Business rule validation
pandoc -t plain output.docx     # Content verification
```

**What This Demonstrates**: Skills use shell as orchestration layer chaining multiple binaries. The shell script acts as build system, not just command executor.

### 2. Validation Pipeline
```bash
./scripts/docx validate FILE    # Standalone validation
./validator/Validator FILE      # Direct binary call
```

**Binary Dependencies**:
- `Validator` (72KB) + DocumentFormat.OpenXml.dll (6.3MB)
- `docx` (13KB shell script)
- `fix_element_order.py` (5KB Python)

### 3. Template Management
```bash
./scripts/docx init             # Environment setup
```

**Actions**:
- Detects dotnet/python3
- Installs missing dependencies
- Initializes `/tmp/docx-work/` working directory
- Copies C# templates (Example.cs, CJKExample.cs)

## IPython Usage Patterns

### 1. Document Editing (Python API)
When editing existing documents (not creating new):

```python
# From references/EditingGuide.md
from scripts.docx_lib.editing import (
    DocxContext,
    add_comment, reply_comment, resolve_comment,
    insert_paragraph, insert_text, propose_deletion,
    enable_track_changes
)

with DocxContext("input.docx", "output.docx") as ctx:
    add_comment(ctx, "Target text", "Comment content")
    insert_text(ctx, "After this", new_text="Inserted")
```

**Integration Point**: Uses `read_file` first (converts docx to markdown for analysis), then ipython for surgical XML edits via lxml.

### 2. Background Generation (HTML→Image)
```python
# generate_backgrounds.py pattern
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 794, 'height': 1123})
    page.set_content(html_content)
    page.screenshot(path='background.png', scale='css')
```

**Key Insight**: Uses ipython + Playwright (via browser_guard.py infrastructure) to generate cover backgrounds, then C# inserts them as floating images.

### 3. Chart Generation (Matplotlib)
```python
# generate_chart.py - for heatmaps/3D only
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
# ... heatmap/radar/3D chart ...
plt.savefig('chart.png', dpi=300)
```

**Constraint**: Only for chart types Word native doesn't support (heatmaps, 3D, radar). Native charts preferred via C# OpenXML.

## Tool Interaction Flow

### Creation Workflow
```
User Request
    ↓
read_file(SKILL.md)         # Load instructions
    ↓
read_file(Example.cs)       # Load template
    ↓
shell: init                 # Setup environment
    ↓
ipython: Edit Program.cs    # Customize template  ← IPython used here
    ↓
shell: build output.docx    # Compile & validate
    ↓
read_file(output.docx)      # Verify with pandoc
    ↓
Deliver with KIMI_REF
```

### Editing Workflow
```
User uploads existing.docx
    ↓
read_file(existing.docx)    # Convert to markdown
    ↓
read_file(EditingGuide.md)  # Load editing API
    ↓
ipython: Editing operations # Direct XML manipulation
    ↓
shell: validate             # Validate output
    ↓
Deliver
```

## Architectural Significance

### 1. **Language Bifurcation**
- **Shell**: Orchestrates compiled binaries (C# toolchain)
- **IPython**: Handles dynamic scripting (Python lxml for XML surgery)

### 2. **Validation as Gatekeeper**
Every shell `build` command includes mandatory validation. The skill cannot produce output without passing:
- OpenXML schema validation (binary)
- Business rule validation (Python)
- Pandoc content verification

### 3. **Template-Driven Code Generation**
IPython is used to modify C# template files (Program.cs), which are then compiled by shell/dotnet. This is meta-programming: Python writes C# that writes docx.

### 4. **Filesystem Conventions**
```
/tmp/docx-work/             # Working directory (ipython writes here)
/mnt/okcomputer/output/     # Final output (shell moves here)
/app/.kimi/skills/docx/     # Skill binaries (read-only)
```

## Critical Steps Formula (Reverse Engineering Insight)

From latency analysis, the DOCX skill follows this critical path:
1. **Read Skill** (~200ms): SKILL.md + Example.cs
2. **IPython Edit** (~500ms): Generate Program.cs
3. **Shell Build** (~2000ms): dotnet build + run + validate
4. **Verify** (~300ms): read_file with pandoc

Total: ~3s per document (dominated by C# compilation).

## Paradigm Implications

The DOCX skill demonstrates **documentation-as-capability**:
- No backend document service
- Agent reads SKILL.md (32KB of instructions)
- Agent generates code (C# or Python)
- Agent executes via shell/ipython
- Validation ensures correctness

The shell and ipython aren't just tools—they're the **runtime environment** for the skill's documented procedures.
