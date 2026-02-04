# DOCX Skill Analysis

The docx skill handles Word document generation through an unusual dual-stack architecture. Unlike typical Python-based document generation, it uses C# with the OpenXML SDK for creation and Python with lxml for editing. This separation reflects different needs: creation benefits from type-safe SDK usage, while editing requires direct XML manipulation.

---

## Dual-Stack Architecture

The skill implements a bifurcated approach based on operation type. Creation uses C# with the OpenXML SDK, which provides automatic package structure management, relationship file generation, Content_Types.xml construction, and type-safe XML element construction. Editing uses Python with lxml, which provides full transparency into document structure, precise control over modifications, and no black-box abstraction layers.

---

## Creation Path

The build process follows a specific pipeline:

```bash
./scripts/docx build [output.docx]
```

1. `dotnet build`: Compilation
2. `dotnet run -- <output path>`: Generation
3. `fix_element_order.py`: XML sequence correction
4. `validator/`: OpenXML schema validation
5. `validate_docx.py`: Business rule validation
6. `pandoc`: Content verification

Path conventions are strict:
- Working directory: `/tmp/docx-work/`
- Output directory: `/mnt/okcomputer/output/`
- Skill directory: `/app/.kimi/skills/docx/`

---

## C# Templates

The skill includes templates for different document types. `Example.cs` provides a complete document example showing standard patterns. `CJKExample.cs` provides 48KB of Chinese, Japanese, and Korean patterns with specific font handling. `Program.cs` is the entry point template, and `KimiDocx.csproj` configures the .NET project.

The C# templates handle element ordering rules that are critical for OpenXML compliance. For example, `sectPr` requires the child sequence: `headerRef` → `footerRef` → `pgSz` → `pgMar`. Tables require `tblPr` → `tblGrid` → `tr`, with the grid being mandatory.

Table column width consistency is enforced:

```csharp
// gridCol width MUST match tcW width
table.Append(new TableGrid(
    new GridColumn { Width = "3600" },  // First column
    new GridColumn { Width = "5400" }   // Second column
));
// ...
new TableCellWidth { Width = "3600", Type = TableWidthUnitValues.Dxa }
```

---

## Editing Path

The Python editing API provides direct XML manipulation:

```python
from scripts.docx_lib.editing import (
    DocxContext,
    add_comment, reply_comment, resolve_comment, delete_comment,
    insert_paragraph, insert_text, propose_deletion,
    reject_insertion, restore_deletion, enable_track_changes
)
```

The `DocxContext` manager handles document state. Comments support threading with replies and resolution. Track changes enables proposal and rejection of edits. The subsystem provides full access to document structure without C# compilation overhead.

---

## Validation Pipeline

The docx skill uses a .NET validator (72KB binary plus 6.9MB of dependencies including DocumentFormat.OpenXml.dll) to check OpenXML schema compliance. This happens after every document generation.

Business rule validation checks document structure against organizational requirements. Element order fixing auto-corrects XML sequences that don't match OpenXML schema. Pandoc verification ensures content round-trips correctly.

---

## Visual Design System

The skill includes a color palette architecture for different document styles:

- **Morandi**: Soft muted tones for artistic, editorial documents
- **Earth tones**: Brown, olive, natural for environmental, organic themes
- **Nordic**: Cool gray, misty blue for minimalist, tech documents
- **Japanese Wabi-sabi**: Gray, raw wood, zen for traditional aesthetics
- **French elegance**: Off-white, dusty pink for luxury, feminine documents
- **Industrial**: Charcoal, rust, concrete for manufacturing
- **Academic**: Navy, burgundy, ivory for research, education

Cover backgrounds are generated via HTML/CSS through Playwright, with device scale factor 2 (794×1123px → 1588×2246px effective), floating anchor with `BehindDoc=true`, and center whitespace for title placement.

---

## File Inventory

The docx skill contains 32 files:
- `SKILL.md` (32KB): Main documentation and instructions
- `references/EditingGuide.md`: Python editing API reference
- `scripts/docx`: Unified CLI entry (13KB shell script)
- `scripts/docx_lib/`: Python library package with business rules, constants, element ordering
- `scripts/docx_lib/editing/`: Document editing subsystem with comments, context, helpers, revisions
- `assets/templates/`: C# generation templates
- `validator/`: .NET OpenXML validator binary and dependencies
