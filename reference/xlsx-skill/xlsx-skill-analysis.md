# The XLSX Skill

The xlsx skill handles Excel spreadsheet generation through a validation-centric workflow. Unlike the docx skill which uses multiple tools, xlsx relies primarily on a single 77MB binary called KimiXlsx that handles validation, PivotTable creation, and formula checking.

---

## Technology Stack

**Primary**: Python + openpyxl + pandas for spreadsheet creation
**Validation**: KimiXlsx CLI tool (compiled binary, 77MB)

The Python layer creates the spreadsheet structure, writes data and formulas, applies styling. The KimiXlsx binary validates the output before delivery.

---

## The KimiXlsx Binary

At 77,001,601 bytes, KimiXlsx is the largest binary in the Kimi system. It provides six commands:

**recheck**: Detects formula errors like `#VALUE!`, `#DIV/0!`, `#REF!`, `#NAME?`, `#NULL!`, `#NUM!`, `#N/A`, zero-value cells, and implicit array formulas. Exit code 0 means no errors, 1 means errors found.

**reference-check**: Validates formula references, detecting out-of-range references, header row inclusion, insufficient aggregate ranges, and inconsistent formula patterns.

**validate**: Performs OpenXML schema validation, checking schema compliance, PivotTable integrity, chart structure, and forbidden functions. Exit code 0 means validation passed, non-zero means failure.

**pivot**: Creates PivotTable with chart. Takes parameters for source range, row fields, value fields, location, and chart type.

**chart-verify**: Verifies charts have data. Exit code 0 means charts are valid, 1 means charts are empty or broken.

**inspect**: Provides structure analysis with JSON output for debugging.

---

## Validation Workflow

The skill enforces a strict per-sheet workflow:

```
For each sheet:
    1. PLAN → Design structure, formulas, references
    2. CREATE → Write data, formulas, styling
    3. SAVE → wb.save()
    4. CHECK → recheck + reference-check → Fix until 0 errors
    5. NEXT → Proceed only when current sheet passes

After ALL sheets:
    6. VALIDATE → validate command → Exit code 0 required
    7. DELIVER → Only validated files
```

Zero tolerance is enforced. Errors in recheck must be fixed before delivery. Non-zero exit codes mean the file cannot be delivered.

---

## Formula Constraints

The skill forbids modern Excel functions that break compatibility with older versions:

- `FILTER()` — Dynamic array function. Alternative: AutoFilter, SUMIF/COUNTIF
- `UNIQUE()` — Dynamic array function. Alternative: Remove Duplicates, COUNTIF helper
- `XLOOKUP()` — New function. Alternative: INDEX + MATCH
- `XMATCH()` — New function. Alternative: MATCH
- `LET()` — New function. Alternative: Helper cells
- `LAMBDA()` — New function. Alternative: Named ranges

These functions work in Excel 365 but crash or return errors in Excel 2019 and earlier. The KimiXlsx validator specifically checks for these and rejects files that use them.

---

## PivotTable Creation Protocol

The workflow for PivotTables is particularly strict:

1. Create ALL sheets with openpyxl (data, cover, styling)
2. Run `pivot` command as **FINAL STEP**
3. **NEVER** open pivot output with openpyxl (corrupts pivotCache)

Correct order:
```
openpyxl creates base.xlsx → pivot command → final.xlsx → validate → DELIVER
```

Wrong order (corrupts file):
```
pivot creates pivot.xlsx → openpyxl opens to add Cover → File broken
```

The pivot binary modifies the Excel file in ways that openpyxl doesn't understand, corrupting the pivotCache if subsequently opened.

---

## Visual Design System

**Minimalist Monochrome** (Default):
- Base: White (#FFFFFF), Black (#000000), Grey shades
- Accent: Blue only (#0066CC, #4A90D9, #E6F0FA)
- Forbidden: All other colors

**Professional Finance** (Financial tasks):
- Background: #ECF0F1 (light gray)
- Header: #1F4E79 (dark blue)
- Regional convention: China (Red=Up, Green=Down), International (Green=Up, Red=Down)

---

## Binary Analysis

```bash
$ file KimiXlsx
KimiXlsx: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV),
          dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
          for GNU/Linux 2.6.32, BuildID[sha1]=771f85eb041bea21c911f46511d0b9727b0b6f68,
          stripped
```

- Format: ELF 64-bit LSB PIE
- Architecture: x86-64
- Size: 77,001,601 bytes (77 MB)
- Stripped: Yes (debug symbols removed)
- PIE: Yes (Position Independent Executable)

Size breakdown:
- OpenXML SDK: ~30 MB
- PivotTable Engine: ~20 MB
- Chart Engine: ~15 MB
- Validation Logic: ~10 MB
- Runtime: ~2 MB

---

## Security Assessment

- Network access: None (offline validation)
- File system: Read-only (input), write (output)
- Execution: Sandboxed
- Stripped: Yes (harder to reverse engineer)

The binary is completely offline. It doesn't download packages or contact external services. It reads Excel files, validates them, and writes output.
