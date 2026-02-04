# XLSX Skill: Shell and IPython Integration Analysis

## Skill Overview
The XLSX skill handles Excel spreadsheet generation with a validation-centric workflow:
- **Creation**: Python + openpyxl (via ipython)
- **Validation**: KimiXlsx binary (77MB, via shell)
- **PivotTables**: KimiXlsx binary command

## Shell Usage Patterns

### 1. Validation Pipeline (KimiXlsx Binary)
The skill centers on a 77MB compiled binary with 6 commands:

```bash
# After EACH sheet creation
/app/.kimi/skills/xlsx/scripts/KimiXlsx recheck output.xlsx
/app/.kimi/skills/xlsx/scripts/KimiXlsx reference-check output.xlsx

# After ALL sheets complete
/app/.kimi/skills/xlsx/scripts/KimiXlsx validate output.xlsx
```

**Binary Commands**:
| Command | Purpose | Exit Code |
|---------|---------|-----------|
| `recheck` | Formula errors (#VALUE!, #DIV/0!, etc.) | 0=pass, 1=fail |
| `reference-check` | Reference anomalies | 0=pass, 1=fail |
| `validate` | OpenXML schema + function compatibility | 0=pass, non-zero=fail |
| `pivot` | Create PivotTable + chart | Varies |
| `chart-verify` | Confirm charts have data | 0=pass, 1=fail |
| `inspect` | Structure analysis (JSON) | 0=pass |

### 2. Per-Sheet Validation Loop
```python
# In ipython (pseudocode)
for sheet in workbook:
    create_sheet(sheet)                    # ipython
    wb.save('/tmp/output.xlsx')            # ipython

    # SHELL CALLS - mandatory after each sheet
    shell(f'recheck {path}')               # Must be 0
    shell(f'reference-check {path}')       # Must be 0

    if errors:
        fix_in_ipython()                   # Back to ipython
        retry
```

**What This Demonstrates**: Validation is not post-processing—it's **interleaved** with creation. Shell commands act as circuit breakers.

### 3. PivotTable Creation
```bash
# FINAL STEP ONLY - after all openpyxl work done
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot     data.xlsx output.xlsx     --source "Sales!A1:F100"     --rows "Category"     --values "Revenue:sum"     --location "Summary!A3"     --chart "bar"
```

**CRITICAL WORKFLOW CONSTRAINT**:
```
CORRECT:
   openpyxl creates base.xlsx (all sheets)
   → pivot command (adds PivotTable)
   → validate
   → DELIVER (do NOT modify again)

WRONG:
   pivot creates pivot.xlsx
   → openpyxl opens to add Cover sheet  ← CORRUPTS pivotCache!
   → File broken
```

## IPython Usage Patterns

### 1. Workbook Construction (Primary)
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Border, Alignment
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import DataBarRule

# Create
wb = Workbook()
ws = wb.active
ws.title = "Data"

# Data with formulas (not static values!)
ws['C2'] = '=A2+B2'                        # Sum formula
ws['D2'] = '=C2/B2*100'                    # Percentage
ws['E2'] = '=SUM(A2:A100)'                 # Aggregation

# Styling
ws['A1'].font = Font(bold=True, color="FFFFFF")
ws['A1'].fill = PatternFill(start_color="333333", fill_type="solid")

# Conditional formatting
ws.conditional_formatting.add('C2:C100', 
    DataBarRule(start_type='min', end_type='max', color='4A90D9'))

# Charts
chart = BarChart()
chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=4))
ws.add_chart(chart, "E2")

wb.save('/mnt/okcomputer/output/data.xlsx')
```

**Formula Mandate**: The skill requires Excel formulas, not calculated values:
```python
# CORRECT
ws['C2'] = '=A2+B2'

# FORBIDDEN
result = value_a + value_b
ws['C2'] = result    # Static value - violates skill principles
```

### 2. Cover Page Creation
```python
# Cover sheet (always first)
cover = wb.create_sheet("Cover", 0)
cover.sheet_view.showGridLines = False

# Merged title
cover.merge_cells('B2:G2')
cover['B2'] = "Report Title"
cover['B2'].font = Font(size=20, bold=True)

# Metrics table
cover['B5'] = "Key Metrics"
cover['B6'] = "Total Revenue"
cover['C6'] = '=Data!E100'  # Formula linking to data sheet
```

### 3. Cross-Sheet References
```python
# VLOOKUP pattern
ws['D2'] = '=IFERROR(VLOOKUP(A2,Data!$G$2:$I$50,3,FALSE),"N/A")'

# Cross-sheet formula
summary['B2'] = '=SUM(Data!C2:C100)'
```

## Tool Interaction Flow

### Standard Workflow
```
Read SKILL.md (925 lines)
    ↓
Plan sheets (Cover, Data, Analysis, Pivot)
    ↓
Sheet 1 (Cover):
    ipython: Create cover styling
    ipython: Save
    shell: recheck → 0 errors?
    shell: reference-check → 0 errors?
    Yes → Next sheet
    ↓
Sheet 2 (Data):
    ipython: Add data + formulas
    ipython: Add charts
    ipython: Save
    shell: recheck → 0?
    shell: reference-check → 0?
    Yes → Next sheet
    ↓
...
Final Validation:
    shell: validate → Exit code 0?
    Yes → Deliver with KIMI_REF
```

### PivotTable Workflow
```
Phase 1: ipython creates ALL sheets except pivot
    - Cover, Raw Data, Analysis sheets
    - Save as base.xlsx
    ↓
Phase 2: shell creates pivot
    KimiXlsx pivot base.xlsx final.xlsx [...params...]
    ↓
Phase 3: shell validates
    KimiXlsx validate final.xlsx → Exit 0
    ↓
Phase 4: Deliver
    (NEVER open final.xlsx in ipython again!)
```

## Architectural Significance

### 1. **Validation-First Design**
Unlike DOCX where validation is final step, XLSX enforces **per-sheet validation**. Shell commands are invoked multiple times during creation, not just at end.

### 2. **Binary Dependency**
The 77MB KimiXlsx binary is the "secret sauce":
- Parses Excel OpenXML natively
- Detects formula errors that openpyxl can't catch
- Validates Excel 365 vs 2019 compatibility
- Creates PivotTables via pure OpenXML SDK (C#)

### 3. **Formula-Centric Philosophy**
The skill mandates formulas over values:
- Enables user modification in Excel
- Self-updating when referenced data changes
- Professional spreadsheet standards
- Validates with `recheck` command

### 4. **Python-Only Creation (Except Pivot)**
Unlike DOCX (C# generation), XLSX uses Python/openpyxl for everything except PivotTable creation. This is because:
- openpyxl handles styling/formulas well
- No compilation step needed (faster iteration)
- PivotTable cache too complex for openpyxl → requires binary

## Critical Constraints

### Forbidden Functions (Detected by validate command)
- `FILTER()`, `UNIQUE()`, `XLOOKUP()`, `XMATCH()` - Excel 365 only
- `LET()`, `LAMBDA()`, `SEQUENCE()` - Dynamic arrays
- `SORT()`, `SORTBY()` - New functions

These cause `validate` to fail with exit code ≠ 0.

### Zero Tolerance Policy
```
recheck error_count: 5 → MUST FIX
recheck zero_value_count: 3 → MUST VERIFY
validate exit code: 1 → CANNOT DELIVER
```

## Paradigm Implications

The XLSX skill demonstrates **validation-as-gatekeeper**:
- Agent has freedom to write any Python/openpyxl code
- Binary validator enforces correctness
- Per-sheet validation prevents error accumulation
- Formula errors are blocking, not warnings

Shell commands serve as **quality checkpoints**, not just utilities. The skill cannot complete without shell validation passing.
